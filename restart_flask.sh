#!/bin/bash

echo "🚀 Flask 앱 재시작 시작..."

# Flask 앱 디렉토리로 이동 (실제 경로로 수정하세요)
cd /home/ubuntu/medical_vlm

echo "📍 현재 디렉토리: $(pwd)"

# 기존 Flask 프로세스 종료
echo "🛑 기존 Flask 프로세스 종료 중..."
pkill -f "python app.py"

# 잠시 대기
sleep 2

# 강제 종료 (필요시)
echo "💥 강제 종료 중..."
pkill -9 -f "python app.py" 2>/dev/null

# 프로세스가 완전히 종료되었는지 확인
if pgrep -f "python app.py" > /dev/null; then
    echo "❌ Flask 프로세스가 여전히 실행 중입니다."
    exit 1
else
    echo "✅ Flask 프로세스가 성공적으로 종료되었습니다."
fi

# Flask 앱 재시작
echo "🔄 Flask 앱 재시작 중..."
nohup python app.py > flask.log 2>&1 &

# 프로세스 ID 저장
echo $! > flask.pid

# 잠시 대기
sleep 3

# 실행 상태 확인
if pgrep -f "python app.py" > /dev/null; then
    echo "✅ Flask 앱이 성공적으로 시작되었습니다!"
    echo "📊 프로세스 정보:"
    ps aux | grep "python app.py" | grep -v grep
    echo "🌐 포트 상태:"
    netstat -tlnp | grep :5000
    echo "📝 로그 파일: flask.log"
    echo "🆔 프로세스 ID: $(cat flask.pid)"
else
    echo "❌ Flask 앱 시작에 실패했습니다."
    echo "📝 로그 확인: tail -f flask.log"
    exit 1
fi
