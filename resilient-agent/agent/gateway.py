import os
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GATEWAY_URL = os.getenv("TRUEFOUNDRY_GATEWAY_URL")
API_KEY = os.getenv("TRUEFOUNDRY_API_KEY")

MODELS = [
    os.getenv("PRIMARY_MODEL"),     # gemini-2.5-flash-lite
    os.getenv("FALLBACK_MODEL_1"),  # nova-micro
    os.getenv("FALLBACK_MODEL_2"),  # nova-lite
]

client = OpenAI(
    api_key=API_KEY,
    base_url=GATEWAY_URL,
)

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def call_model(model: str, messages: list, temperature: float = 0.7) -> str:
    logger.info(f"Trying model: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1000,
    )
    return response.choices[0].message.content

def call_with_fallback(messages: list, temperature: float = 0.7) -> dict:
    for i, model in enumerate(MODELS):
        try:
            result = call_model(model, messages, temperature)
            logger.info(f"Success with model: {model}")
            return {
                "content": result,
                "model_used": model,
                "fallback_level": i
            }
        except Exception as e:
            logger.warning(f"Model {model} failed: {str(e)}")
            if i == len(MODELS) - 1:
                logger.error("All models failed!")
                raise Exception(f"All models exhausted. Last error: {str(e)}")
            logger.info(f"Falling back to next model...")
    
if __name__ == "__main__":
    messages = [{"role": "user", "content": "Say hello and which model you are."}]
    result = call_with_fallback(messages)
    print(f"\nResponse: {result['content']}")
    print(f"Model used: {result['model_used']}")
    print(f"Fallback level: {result['fallback_level']}")