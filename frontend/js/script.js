document.addEventListener('DOMContentLoaded', () => {
    const sourceText = document.getElementById('source-text');
    const targetPersona = document.getElementById('target-persona');
    const convertBtn = document.getElementById('convert-btn');
    const resultText = document.getElementById('result-text');
    const charCount = document.getElementById('char-count');
    const copyBtn = document.getElementById('copy-btn');
    const feedbackFooter = document.querySelector('.feedback-footer');

    // 실시간 글자 수 체크
    sourceText.addEventListener('input', () => {
        const length = sourceText.value.length;
        charCount.textContent = `${length}/500`;
        
        if (length > 500) {
            charCount.style.color = '#D0021B'; // Error color
        } else {
            charCount.style.color = '#6c757d';
        }
    });

    // 변환 버튼 클릭 이벤트
    convertBtn.addEventListener('click', async () => {
        const text = sourceText.value.trim();
        const target = targetPersona.value;

        if (!text) {
            alert('변환할 내용을 입력해주세요.');
            return;
        }

        // 로딩 상태 표시
        convertBtn.disabled = true;
        convertBtn.textContent = '변환 중...';
        resultText.classList.add('result-placeholder');
        resultText.textContent = 'AI가 말투를 변환하고 있습니다. 잠시만 기다려주세요...';
        feedbackFooter.style.display = 'none';
        copyBtn.disabled = true;

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, target }),
            });

            const data = await response.json();

            if (response.ok) {
                // 결과 표시
                resultText.classList.remove('result-placeholder');
                resultText.textContent = data.converted;
                copyBtn.disabled = false;
                feedbackFooter.style.display = 'flex';
            } else {
                throw new Error(data.error || '변환에 실패했습니다.');
            }
        } catch (error) {
            console.error('Error:', error);
            resultText.textContent = `오류가 발생했습니다: ${error.message}\n잠시 후 다시 시도해주세요.`;
            resultText.style.color = '#D0021B';
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = '말투 변환하기';
        }
    });

    // 복사하기 버튼 이벤트
    copyBtn.addEventListener('click', () => {
        const textToCopy = resultText.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '복사 완료!';
            copyBtn.style.color = '#50E3C2'; // Success color
            copyBtn.style.borderColor = '#50E3C2';

            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.color = '';
                copyBtn.style.borderColor = '';
            }, 2000);
        }).catch(err => {
            console.error('복사 실패:', err);
            alert('클립보드 복사에 실패했습니다.');
        });
    });

    // 피드백 버튼 이벤트
    const feedbackBtns = document.querySelectorAll('.feedback-btns .icon-btn');
    feedbackBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const feedback = btn.textContent === '👍' ? 'helpful' : 'not_helpful';
            const target = targetPersona.value;
            const text = resultText.textContent;

            try {
                const response = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text, target, feedback }),
                });

                if (response.ok) {
                    alert('피드백을 보내주셔서 감사합니다!');
                    feedbackFooter.style.display = 'none'; // 한 번 보내면 숨김
                }
            } catch (error) {
                console.error('Feedback Error:', error);
            }
        });
    });
});