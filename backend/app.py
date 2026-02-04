import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

# Flask 앱 설정: frontend 폴더를 정적 파일 폴더로 지정
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, '..', 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

# CORS 설정: 모든 도메인에서의 요청 허용 (개발 환경)
CORS(app)

# Groq 클라이언트 초기화
api_key = os.getenv("GROQ_API_KEY")
client = None
if api_key:
    client = Groq(api_key=api_key)
else:
    print("Warning: GROQ_API_KEY is not set in environment variables.")

@app.route('/')
def index():
    """메인 페이지 서빙 (index.html)"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인 엔드포인트"""
    return jsonify({"status": "ok", "message": "BizTone Converter API is running"})

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """
    텍스트 변환 엔드포인트
    Request Body: {
        "text": "변환할 텍스트",
        "target": "boss" | "colleague" | "customer"
    }
    """
    if not client:
        return jsonify({"error": "Groq API client is not initialized"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    text = data.get('text')
    target = data.get('target', 'boss') # 기본값: 상사

    if not text:
        return jsonify({"error": "Text is required"}), 400

    # 타겟에 따른 시스템 프롬프트 설정
    system_prompts = {
        "boss": "당신은 비즈니스 커뮤니케이션 전문가입니다. 입력된 문장을 상사에게 보고하기 적합한 정중하고 격식 있는 말투로 변환해주세요.",
        "colleague": "당신은 비즈니스 커뮤니케이션 전문가입니다. 입력된 문장을 타팀 동료에게 협업을 요청하거나 정보를 공유하기 적합한 정중하지만 친근한 존댓말 말투로 변환해주세요.",
        "customer": "당신은 비즈니스 커뮤니케이션 전문가입니다. 입력된 문장을 고객에게 응대하기 적합한 공식적이고 극존칭을 사용하는 정중한 말투로 변환해주세요."
    }

    prompt = system_prompts.get(target, system_prompts["boss"])

    try:
        # Groq API 호출 (최신 Llama 3.3 모델로 변경)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama-3.3-70b-versatile", # <--- 여기서 모델을 최신으로 교체했습니다!
            temperature=0.5,
            max_tokens=1024,
        )

        converted_text = chat_completion.choices[0].message.content.strip()

        return jsonify({
            "original": text,
            "converted": converted_text,
            "target": target
        })

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return jsonify({"error": "Failed to convert text", "details": str(e)}), 500

if __name__ == '__main__':
    # 5000번 포트로 실행
    app.run(host='127.0.0.1', port=5000)