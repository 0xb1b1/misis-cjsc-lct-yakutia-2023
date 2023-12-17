import os
import random
from tqdm.auto import tqdm

tqdm.pandas()
import re

import pandas as pd
import numpy as np
from datasets import Dataset

import scipy
import sklearn

import torch
from torch.utils.data import DataLoader
from transformers import AutoModel, AutoTokenizer

import faiss


def seed_everything(seed: int,
                    use_deterministic_algos: bool = False) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.use_deterministic_algorithms(use_deterministic_algos)
    random.seed(seed)


class Summarizer:
    def __init__(self,
                 model: AutoModel,
                 tokenizer: AutoTokenizer,
                 device: str = "cuda"):
        super().__init__()
        self.device = device

        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()
        self.model.to(self.device)

        self.WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

    def summarize(self, text):
        input_ids = self.tokenizer(
            [self.WHITESPACE_HANDLER(text)],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )["input_ids"].to(self.device)

        output_ids = self.model.generate(
            input_ids=input_ids,
            max_length=256,
            no_repeat_ngram_size=2,
            num_beams=4
        )[0]

        summary = self.tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        return summary


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def mongo_to_pandas(mongo_return):
    mongo_return = list(mongo_return)
    urls = []
    contents = []

    for el in list(mongo_return):
        urls.append(el.url)
        contents.append(el.content)

    return pd.DataFrame({"url": urls, "content": contents})


class Retriever:
    def __init__(
            self,
            model: AutoModel,
            tokenizer: AutoTokenizer,
            summarizer,
            ood_model,
            db,
            d: int,
            k: int,
            batch_size: int = 1,
            device: str = "cuda",
    ):
        super().__init__()
        self.device = device

        self.model = model
        self.model.eval()
        self.model.to(self.device)
        self.tokenizer = tokenizer
        self.summarizer = summarizer
        self.ood_model = ood_model

        self.k = k
        self.batch_size = batch_size

        self.index = faiss.IndexFlatL2(d)
        self.db = db

    def add(self, new_samples):
        """
        Сюда приходит csv с новыми записями
        """

        df = mongo_to_pandas(new_samples)
        df["short_text"] = df["content"].progress_apply(self.summarizer.summarize)

        dataset = Dataset.from_pandas(df)
        dataset = dataset.map(lambda sample: self._preprocess_text(sample['short_text']))
        dataset = dataset.remove_columns(['short_text'])
        dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
        dataloader = DataLoader(dataset, batch_size=self.batch_size)

        embeddings = []

        for batch in tqdm(dataloader):
            input_ids, attention_masks = batch["input_ids"].squeeze(dim=1), batch["attention_mask"].squeeze(dim=1)
            input_ids, attention_masks = input_ids.to(self.device), attention_masks.to(self.device)

            with torch.no_grad():
                # print(input_ids.shape, attention_masks.shape)
                output = mean_pooling(
                    self.model(
                        input_ids=input_ids,
                        attention_mask=attention_masks,
                    ), attention_masks)

            embeddings.append(output.cpu())

        embeddings = torch.cat(embeddings, dim=0).numpy()

        self.index.add(embeddings)
        torch.cuda.empty_cache()

    def get_indexer_size(self) -> int:
        return self.index.ntotal

    def save_index(self, path: str = "/data/index.bin"):
        faiss.write_index(self.index, path)

    def load_index(self, path: str = "/data/index.bin"):
        self.index = faiss.read_index(path)

    def _preprocess_text(self, text):
        out = self.tokenizer.encode_plus(
            text,
            max_length=512,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return out

    def _get_embedding(self, sample):
        input_ids = sample["input_ids"]
        if len(input_ids.shape) < 2:
            input_ids.unsqueeze(dim=0)

        attention_mask = sample["attention_mask"]
        if len(attention_mask.shape) < 2:
            input_ids.unsqueeze(dim=0)

        with torch.no_grad():
            return mean_pooling(
                self.model(
                    input_ids.to(self.device), attention_mask.to(self.device)
                ),
                attention_mask.to(self.device),
            ).cpu().numpy()

    def query(self, text):
        sample = self._preprocess_text(text)
        embedding = self._get_embedding(sample)
        ood_score = int(self.ood_model.predict(embedding.tolist())[0][0])

        torch.cuda.empty_cache()

        if ood_score == 0:
            dictances, inds = self.index.search(embedding, k=self.k)

            ret = self.db.find_by(
                {"seq_id": {"$in": inds[0].tolist()}}
            )

            return mongo_to_pandas(ret), ood_score
        else:
            return ood_score


class Chat:
    def __init__(self, model, tokenizer, generation_config, retriever, k: int = 3, device: str = "cuda"):
        self.device = device

        self.model = model
        self.model.eval()
        self.model.to(self.device)
        self.tokenizer = tokenizer

        self.generation_config = generation_config
        self.retriever = retriever
        self.k = k

        self.request_type = {
            0: 'chat_bot',
            1: 'events',
            2: 'weather',
            3: 'traffic_jam',
            4: 'mini_app',
            5: 'social_networks',
            6: 'trash'
        }

    @staticmethod
    def _remove_punct(text):
        text = "".join([char for char in text if char.isalpha() or char == " "])
        return text

    @staticmethod
    def _form_prompt(text, retrieved):
        texts = retrieved["content"].tolist()

        prompt = f"<SC6>Текст: {texts[0]}\nВопрос: {text}"
        # print(prompt)
        return prompt

    def generate(self, prompt):
        data = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        try:
            output_ids = self.model.generate(
                **data,
                generation_config=self.generation_config,
            )[0]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            return None

        torch.cuda.empty_cache()

        out = self.tokenizer.decode(output_ids.tolist(), skip_special_tokens=True)
        return out

    def postprocess(self, generated):
        generated = generated.strip()[len('<extra_id_0>'):].strip()
        if "Ответ: " in generated:
            generated = generated.split("Ответ: ")[1]
            if "Вопрос: " in generated:
                return generated.split("Вопрос: ")[0]
            return generated
        # else:
        #     return generated
        return generated

    def answer(self, message):
        torch.cuda.empty_cache()

        retrieved_samples = self.retriever.query(message)

        if isinstance(retrieved_samples, int):
            request_type = retrieved_samples
            # print(request_type)
            return self.request_type[request_type], """
            Пока что я не могу ответить на данный вопрос — мне не хватает данных. Но вы можете позвонить в администрацию города Мирный или дождаться ответа оператора. 
            Телефон для связи: 8 (41136) 6-19-19
            """

        retrieved_samples, request_type = retrieved_samples
        # print(type(retrieved_samples['url'][0]))

        prompt = self._form_prompt(message, retrieved_samples)

        generated = self.generate(prompt)
        torch.cuda.empty_cache()
        if isinstance(generated, type(None)):
            return self.request_type[request_type], """Кажется что-то сломалось.
                      Но мы уже знаем и стараемся починить — напишите нам позже"""

        return self.request_type[request_type], f"{self.postprocess(generated)}\n\nНа основе документа {retrieved_samples['url'][0]}"
