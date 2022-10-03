from data.contexts_and_questions import CLASS_NAME_TEXT, QuestionBody
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from transformers import pipeline

destilbert_qa = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')

class_names = list()
qs = list()
ans = list()
scores = list()

for class_name in CLASS_NAME_TEXT.keys():
    print(class_name)
    qb = QuestionBody(class_name)
    context = CLASS_NAME_TEXT.get(class_name)

    for question in qb.general_questions:
        answer = destilbert_qa(question=question, context=context)
        print('Question:' + question)
        print(f"Answer: '{answer['answer']}' with score {answer['score']}")
    for question in qb.specific_questions:
        answer = destilbert_qa(question=question, context=context)
        # class_names.append(class_name)
        # qs.append(question)
        # ans.append(answer['answer'])
        # scores.append(answer['score'])
        print('Question:' + question)
        print(f"Answer: '{answer['answer']}' with score {answer['score']}")
    print('\n')


def qa(question, answer_text, model, tokenizer):
    inputs = tokenizer.encode_plus(question, answer_text, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    text_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    # print(text_tokens)
    outputs = model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    answer_start = torch.argmax(
        answer_start_scores
    )  # Get the most likely beginning of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    # Combine the tokens in the answer and print it out.""
    answer = answer.replace("#", "")

    print(f"Question: {question}")
    print(f"Answer: {answer}")
    return answer


electra_tokenizer = AutoTokenizer.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")
electra_model = AutoModelForQuestionAnswering.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")

class_names = list()
qs = list()
ans = list()
scores = list()

for class_name in CLASS_NAME_TEXT.keys():
    print(class_name)
    qb = QuestionBody(class_name)
    context = CLASS_NAME_TEXT.get(class_name)

    for question in qb.general_questions:
        qa(question, context, electra_model, electra_tokenizer)
    for question in qb.specific_questions:
        qa(question, context, electra_model, electra_tokenizer)

    print('\n')
