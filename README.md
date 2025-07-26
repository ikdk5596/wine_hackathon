# Wine hackathon

# Application Explanation
요즘, 점차 모든 것이 공유되고 하나의 인터넷으로 전세계가 연결 되면서 해킹 사건이 큰 사회적 문제로 대두되고 있습니다. 대부분의 회사가 보안을 강화하면서 이를 차단하려 하지만, 해킹의 원천 차단은 불가능한 것이 현실이라고 생각하였습니다.

본 팀은 이러한 이슈 사항을 해결하기 위해서 다음의 보안 메신저를 생각하였습니다.
1. Edge AI를 활용하여 같은 Parameter를 공유하고 있다면 이미지 등을 전송할 때 실시간으로 latent domain으로 압축합니다.
2. 압축된 latent를 사용자의 private키를 통해 생성된 public key로 암호화합니다.
3. 암호화된 파일을 전송합니다.
4. 개인은 해당 파일을 저장할 때 본인 PC의 고유 번호를 통해서 저장하여 혹시 파일이 탈취 당하더라도 해당 파일을 복호화 하지 못하도록 합니다.

# Team members
김상홍 sanghongkim@korea.ac.kr  
이병호 unlike96@korea.ac.kr  
유경현 seven1705@korea.ac.kr  
이승주 joon8958@gmail.com  
김건우 bbosam2004@gmail.com  

# Dependency
python>=3.11  
torch==2.6.0  
numpy  
diffusers  

# 실행 및 사용 지침
부탁해용

# License
Copyright 2025 Wine Lab

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
