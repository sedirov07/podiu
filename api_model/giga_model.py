from langchain_community.chat_models import GigaChat


class GigaModel:
    def __init__(self, auth_key, scope, model_name, searcher):
        self.params = {'credentials' :auth_key, 'scope': scope, 'verify_ssl_certs': False, 'model': model_name}
        self.llm = GigaChat(**self.params, temperature=0.01, max_length=3800)
        self.searcher = searcher

    async def chat(self, text):
        try:
            res = self.llm.invoke(text)
            return res.content
        except Exception as e:
            print(e)
            return 'Error'

    async def get_rag_result(self, question):
        try:
            new_question = await self.llm.ainvoke(f'A question has been sent to you from a user. If it\'s not accurate enough, rephrase it. Give me only new or old question.\nQuestion: {question}')
            new_question = new_question.content
            if len(new_question.split(':')) == 2:
                new_question = new_question.split(':')[-1].strip()
        except Exception as e:
            print(e)
            new_question = question

        chunks = [c[0] for c in await self.searcher.search_query(new_question)]
        system_prompt = 'You are an assistant at the Preparatory Department for Foreign Students of the Ural Federal University. Your goal is to answer the questions that the applicants ask you. Don\'t give me a detailed answer.'

        if len(chunks):
            documents = '\n'.join([f'Question: {c.metadata["question"]}\tAnswer: {c.page_content}' for c in chunks])
            task = f'Using the information provided below to answer the \nFAQ question: {documents}'
            task = task[:10000] + f'\nQuestion: {new_question}'
            query = system_prompt + '\n' + task
        else:
            task = f'\nQuestion: {new_question}'
            query = system_prompt + task

        try:
            res = await self.llm.ainvoke(query)
            # print(query)
            return res.content
        except Exception as e:
            print(e)
            return ''
