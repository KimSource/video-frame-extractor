# Video Frame Extractor

FFmpeg으로 동영상 프레임을 추출하는 간단한 Windows GUI 도구입니다.

다른 언어로 읽기: [English](README.md), [한국어](README.ko-KR.md)

## 주요 기능

- 일정한 프레임 간격 또는 지정한 프레임 목록을 기준으로 추출
- JPG, PNG, WebP 형식으로 저장
- JPG와 WebP 품질 조절 및 무손실 WebP 출력
- 추출 전에 실행할 FFmpeg 명령 확인

## 요구 사항

- Windows
- 애플리케이션 옆에 FFmpeg를 배치하거나 시스템 `PATH`에 등록
- 소스에서 실행할 경우 Tkinter가 포함된 Python

기본적으로 애플리케이션은 애플리케이션 또는 소스 파일 옆의 다음 상대 경로에서
FFmpeg를 찾습니다.

```text
video-frame-extractor/
├─ main.py
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

또는 시스템 `PATH`에 등록된 `ffmpeg.exe`를 사용할 수 있습니다. 실행 후 GUI의
FFmpeg 섹션에서 사용할 실행 파일을 선택합니다.

## 소스에서 실행

1. Python을 설치하고 `python` 명령이 `PATH`에 등록되어 있는지 확인합니다.
2. [FFmpeg](https://ffmpeg.org/download.html)의 Windows 빌드를 다운로드하여 위 구조에 맞게 배치합니다.
3. 가상환경을 생성합니다.

   ```powershell
   .\setup-venv.bat
   ```

4. 애플리케이션을 실행합니다.

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

애플리케이션 실행에는 Python 표준 라이브러리만 사용합니다.

## 테스트 실행

개발자용 자동 테스트를 실행하려면 프로젝트 루트에서 다음 명령을 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

테스트는 Python 표준 라이브러리의 `unittest`를 사용합니다.

## 실행 파일 빌드

가상환경을 설정하고 선언된 빌드 의존성을 설치합니다.

```text
.\setup-venv.bat
```

그다음 다음 명령을 실행합니다.

```powershell
.\build.bat
```

실행 파일은 `dist\main.exe`에 생성됩니다. 패키징된 애플리케이션을 실행하기 전에 `ffmpeg` 디렉터리를 실행 파일 옆에 복사합니다.

```text
dist/
├─ main.exe
└─ ffmpeg/
   └─ bin/
      └─ ffmpeg.exe
```

미리 빌드된 버전은 [Releases 페이지](https://github.com/KimSource/video-frame-extractor/releases)에서 받을 수 있습니다.

## 라이선스

이 프로젝트는 [BSD Zero Clause License](LICENSE)로 배포됩니다.
