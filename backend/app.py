import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask 앱 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, '..', 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

CORS(app)

# Groq 클라이언트 초기화
api_key = os.getenv("GROQ_API_KEY")
client = None
if api_key:
    client = Groq(api_key=api_key)
    logger.info("Groq client initialized successfully.")
else:
    logger.warning("GROQ_API_KEY is not set.")

@app.route('/')
def index():
    """메인 페이지 서빙"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/convert', methods=['POST'])
def convert_text():
    if not client:
        return jsonify({"error": "API 키 설정이 필요합니다."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    text = data.get('text')
    target = data.get('target', 'boss')

    # 페르소나별 시스템 프롬프트
    system_prompts = {
        "boss": "상사에게 보고하는 정중한 격식체(-합니다)로 변환하세요. 두괄식 구조를 사용하세요.",
        "colleague": "타팀 동료에게 보내는 친절하고 협력적인 어투로 변환하세요. '해요체'를 권장합니다.",
        "customer": "외부 고객에게 보내는 극존칭의 공식적인 말투로 변환하세요."
    }

    prompt = system_prompts.get(target, system_prompts["boss"])

    try:
        # 민희님이 확인하신 Kimi K2 모델 ID를 적용했습니다!
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"다음 문장을 요청된 톤으로 변환해줘: \"{text}\""}
            ],
            model="moonshotai/kimi-k2-instruct-0905", 
            temperature=0.3,
            max_tokens=1024,
        )

        if not chat_completion.choices:
            raise ValueError("No response from AI")

        converted_text = chat_completion.choices[0].message.content.strip()
        
        # 따옴표 제거 로직
        if converted_text.startswith('"') and converted_text.endswith('"'):
            converted_text = converted_text[1:-1]

        return jsonify({
            "converted": converted_text
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "변환 중 오류 발생", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)