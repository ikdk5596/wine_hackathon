# 🍷 Wine Hackathon

## Overview

오늘날 전 세계가 인터넷으로 연결되며 사이버 보안은 그 어느 때보다 중요한 이슈로 부상하고 있습니다. 많은 기업들이 보안 강화를 위해 노력하고 있지만, 해킹을 원천적으로 차단하는 것은 여전히 어려운 과제입니다.

본 프로젝트는 이러한 문제를 해결하기 위한 **AI 지능형 보안 메신저 시스템**을 제안합니다. 이미지 전송 과정에서 **디바이스 고유 식별자를 이용한 Edge AI 암호화**를 활용하여 높은 수준의 데이터 보안을 구현합니다.또한 데이터를 latent domain에서 압축하여 전송함으로써, 데이터의 크기를 최소화하고 통신 자원을 효율적으로 사용합니다.

### Key Features

1. **Edge AI 기반 인코딩**  
   클라이언트 간 동일한 모델 파라미터를 공유함으로써, 전송 대상 이미지를 단말에서 실시간으로 latent domain으로 인코딩합니다. 이를 통해 원본 이미지 노출 없이 압축된 표현만을 추출할 수 있습니다.

2. **비대칭키 기반 데이터 암호화**  
   생성된 latent vector는 사용자 단말에서 생성된 private key를 기반으로 도출한 public key를 사용해 암호화됩니다. 이 과정은 수신자 외에는 데이터를 해독할 수 없도록 보장합니다.

3. **암호화 데이터 전송 및 탈취 대응**  
   암호화된 데이터는 네트워크를 통해 전송되며, 설령 전송 중 데이터가 탈취되더라도 복호화가 불가능하여 실질적인 정보 유출을 방지할 수 있습니다. 또한 디바이스의 고유 식별자(HW ID 등)를 확인하며, 등록된 장치에서만 복호화가 가능하도록 설계되어 있습니다. 이를 통해 타 기기에서의 무단 복호화를 원천적으로 차단합니다.

---

## Team Members

| 이름     | 이메일 |
|----------|--------|
| 김상홍   | sanghongkim@korea.ac.kr |
| 이병호   | unlike96@korea.ac.kr     |
| 유경현   | seven1705@korea.ac.kr    |
| 김건우   | bbosam2004@gmail.com     |
| 이승주   | joon8958@gmail.com       |

---

## Dependencies

```text
Python >= 3.11  
pip >= 23.0
```
Python 3.11 이상과 pip 23.0 이상이 필요합니다. 추가 라이브러리는 requirements.txt에 명시되어 있습니다.


## Getting Started

### GUI 프로그램
채팅 형식의 사용자 인터페이스를 제공하는 GUI 프로그램입니다. 사용자는 친구 목록에서 대상을 선택하고, 이미지 파일을 업로드하여 암호화된 메시지를 전송할 수 있습니다.
1. **프로젝트 루트에서 GUI 디렉토리로 이동**  
   ```bash
   cd gui
   ```
2. **(선택 사항) 가상환경 생성 및 활성화**
   * **venv 방식**
   ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
   ``` 
   * **Anaconda 방식**
   ```bash
    # Windows/Linux/Mac
    conda create -n wine_hackathon_app python=3.11
    conda activate wine_hackathon_app
   ```
3. **필요한 라이브러리 설치**  
   ```bash
    pip install -r requirements.txt
   ```
4. **응용프로그램 실행**  
   ```bash
    python main.py
   ```
5. **사용법은 [사용 영상](https://youtu.be/7b1k2Z5g0a4)에서 확인할 수 있습니다.**

### CLI 프로그램
CLI(Command Line Interface) 프로그램으로, 이미지 파일을 암호화하고 복호화하는 기능을 제공합니다. 응용 프로그램의 핵심 로직을 구현하며, 이미지 파일을 암호화된 latent vector로 변환하고 이를 복호화할 수 있습니다.
1. **프로젝트 루트에서 CLI 디렉토리로 이동**  
   ```bash
   cd cli
   ```
2. **(선택 사항) 가상환경 생성 및 활성화**
   * **venv 방식**
   ```bash
    # Windows
    python -m venv venv
    source .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
   ``` 
   * **Anaconda 방식**
   ```bash
    # Windows/Linux/Mac
    conda create -n wine_hackathon_core python=3.11
    conda activate wine_hackathon_core
   ```
3. **필요한 라이브러리 설치**  
   ```bash
    pip install -r requirements.txt
   ```
4. **암호화 실행**
   이미지가 latent 벡터로 변환되어 암호화된 파일로 저장됩니다.
   - 입력 이미지 파일: `{input_image.png}`
   - 암호화 키: `{key}` (고유한 비밀 키로, 사용자가 입력)
   - 암호화된 latent 벡터 파일: `{encrypted_latent.pt}`
   ```bash
    python encrypt.py input_image.png --key={key}
   ```
5. **복호화 실행**  
    암호화된 latent 벡터 파일을 복호화하여 원본 이미지로 복원합니다.
    - 암호화된 latent 벡터 파일: `{encrypted_latent.pt}`
    - 복호화 키: `{key}` (암호화 시 사용한 동일한 키)
    - 복호화된 이미지 파일: `{reconstructed_image.png}`
   ```bash
    python decrypt.py encrypted_latent.pt --key={key}
   ```

## License
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.