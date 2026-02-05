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
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    logger.info("Groq client initialized successfully.")
else:
    logger.warning("GROQ_API_KEY is not set in environment variables.")

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
        logger.error("Groq API client is not initialized")
        return jsonify({"error": "Groq API client is not initialized"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    text = data.get('text')
    target = data.get('target', 'boss') # 기본값: 상사

    if not text:
        return jsonify({"error": "Text is required"}), 400

    # 타겟에 따른 시스템 프롬프트 설정 (PRD 기반 - 프롬프트 엔지니어링 강화)
    system_prompts = {
        "boss": (
            "당신은 유능하고 정중한 비즈니스 커뮤니케이션 전문가입니다. "
            "사용자의 거친 표현이나 일상적인 말투를 상사(Upward)에게 보고하기 적합한 '정중한 격식체(-합니다)'로 변환하세요.\n"
            "지침:\n"
            "1. 결론부터 명확하게 제시하는 '두괄식' 구조를 사용하세요.\n"
            "2. 상사에게 신뢰감을 줄 수 있는 전문적인 용어를 사용하세요.\n"
            "3. '부탁드립니다', '검토 요청드립니다' 등 정중한 표현을 필수적으로 포함하세요.\n"
            "4. 불필요한 사족은 줄이고 핵심 위주로 구성하세요."
        ),
        "colleague": (
            "당신은 협업 능력이 뛰어난 비즈니스 커뮤니케이션 전문가입니다. "
            "사용자의 표현을 타팀 동료(Lateral)에게 전달하기 적합한 '친절하고 상호 존중하는 어투'로 변환하세요.\n"
            "지침:\n"
            "1. '부탁드립니다', '도움 주시면 감사하겠습니다' 등 협조를 구하는 톤을 유지하세요.\n"
            "2. 요청 사항(What)과 마감 기한(When)이 포함되어 있다면 이를 명확히 강조하세요.\n"
            "3. 상대방의 상황을 배려하는 문구를 포함하여 유연한 협업 관계를 구축하세요.\n"
            "4. 너무 딱딱하지 않되 예의를 갖춘 '해요체' 또는 '합쇼체'를 적절히 섞어 사용하세요."
        ),
        "customer": (
            "당신은 최고의 서비스 마인드를 가진 비즈니스 커뮤니케이션 전문가입니다. "
            "사용자의 입력을 외부 고객(External)에게 전달하기 적합한 '극존칭'과 '신뢰감' 있는 말투로 변환하세요.\n"
            "지침:\n"
            "1. 고객의 기분을 존중하고 기업의 전문성을 보여주는 공식적인 말투를 사용하세요.\n"
            "2. 안내, 공지, 사과 등 상황에 맞는 표준화된 비즈니스 서식(인사말-본문-맺음말)을 따르세요.\n"
            "3. '안내해 드립니다', '불편을 드려 죄송합니다', '최선을 다하겠습니다' 등의 정중한 표현을 사용하세요.\n"
            "4. 고객에게 신뢰를 줄 수 있도록 문장이 모호하지 않고 명확해야 합니다."
        )
    }

    prompt = system_prompts.get(target, system_prompts["boss"])
    logger.info(f"Conversion Start - Target: {target}, Input Length: {len(text)}")

    try:
        # Groq API 호출
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"다음 문장을 요청된 톤으로 변환해줘: \"{text}\""
                }
            ],
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.3,
            max_tokens=1024,
        )

        if not chat_completion.choices or not chat_completion.choices[0].message.content:
            raise ValueError("Empty response from AI model")

        converted_text = chat_completion.choices[0].message.content.strip()
        
        # 만약 AI가 답변에 따옴표를 포함했다면 제거 (가끔 문장만 달라고 해도 따옴표를 넣는 경우가 있음)
        if converted_text.startswith('"') and converted_text.endswith('"'):
            converted_text = converted_text[1:-1]
        
        logger.info(f"Conversion Success - Output Length: {len(converted_text)}")

        return jsonify({
            "original": text,
            "converted": converted_text,
            "target": target
        })

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}", exc_info=True)
        error_msg = "텍스트 변환 중 오류가 발생했습니다."
        if "rate_limit" in str(e).lower():
            error_msg = "요청 한도가 초과되었습니다. 잠시 후 다시 시도해주세요."
        elif "authentication" in str(e).lower() or "api_key" in str(e).lower():
            error_msg = "API 인증 오류가 발생했습니다. 관리자에게 문의하세요."
            
        return jsonify({
            "error": error_msg,
            "details": str(e) if app.debug else "Internal Server Error"
        }), 500

@app.route('/api/feedback', methods=['POST'])
def save_feedback():
    """
    사용자 피드백 저장 엔드포인트 (FR-06)
    Request Body: {
        "text": "변환된 텍스트",
        "target": "boss" | "colleague" | "customer",
        "feedback": "helpful" | "not_helpful"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400
    
    # 실제 운영 환경이라면 DB에 저장하겠지만, 현재는 로그로 기록하여 분석
    logger.info(f"Feedback Received - Target: {data.get('target')}, Feedback: {data.get('feedback')}")
    
    return jsonify({"status": "ok", "message": "Feedback saved successfully"})

if __name__ == '__main__':
    # 5000번 포트로 실행
    app.run(host='127.0.0.1', port=5000)