# 로봇 학습 복습 노트

갱신: 2026-10-05 · Python은 익숙하고 로봇은 처음인 수준에 맞춘다.

실습 방식: **주석이 있는 전체 코드를 채팅에서 받기 → 그대로 직접 입력 → 실행·확인**. 코드를 여러 조각으로 나누지 않는다. 실행 후에는 설정 하나를 바꾸어 값과 움직임의 관계를 확인한다.

**Isaac Sim**은 물리 시뮬레이터, **Isaac Lab**은 그 위에서 로봇 제어·학습 실험을 구성하는 도구다.

## 실행 준비

기존 시뮬레이터 창을 닫고 Anaconda Prompt에서:

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
```

아래 실습별 명령을 실행한다. 프로젝트 목표는 [README](C:/makerobot/README.md), 설치 기록은 [INSTALLATION](C:/makerobot/INSTALLATION.md)에 있다.

## 1. 가상 시간 — 빈 장면

```bat
isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

**`sim.step()` 한 번이 가상 세계의 시간을 한 단계 진행한다.**

- `dt=0.01`이면 100스텝 = 가상 시간 1초다. PC에서 실제로 걸리는 시간과는 다르다.
- `sim.reset()`은 장면의 물리 계산을 준비한다.
- 화면의 격자는 물체를 받치는 물리 바닥이 아니다.

확인 완료: 빈 창과 `[INFO]: Setup complete...` 문구.

## 2. 중력과 접촉 — 상자 낙하

[실습 코드](C:/makerobot/scripts/01_drop_cube.py)

```bat
isaaclab.bat -p C:\makerobot\scripts\01_drop_cube.py
```

**강체**는 형태가 변하지 않는다고 가정한 물체, **충돌 형상**은 접촉을 계산하는 경계다. 상자를 강체로 만들고 상자·바닥 양쪽에 충돌 형상을 준다.

이번 장면은 +z가 위쪽이고 길이 단위는 m다. 한 변 0.2m인 상자의 중심을 높이 1m에서 놓는다. 바닥 윗면은 z=0이므로 정지한 상자 중심은 약 0.1m다.

사용자가 확인한 출력:

```text
t=0.10 s | center z=0.946 m | vz=-0.981 m/s
t=0.20 s | center z=0.794 m | vz=-1.962 m/s
t=0.30 s | center z=0.544 m | vz=-2.943 m/s
t=0.40 s | center z=0.196 m | vz=-3.924 m/s
t=0.50 s | center z=0.100 m | vz=-0.000 m/s
t=0.60 s | center z=0.100 m | vz=-0.000 m/s
```

- **낙하 중:** 0.1초마다 속도가 -0.981m/s 변한다. 가속도는 `-0.981 / 0.1 = -9.81m/s²`다.
- **접촉 후:** 중심 높이 0.1m, 속도 약 0. 중력이 사라진 것이 아니라 바닥이 받쳐 준다. `-0.000`은 약 0으로 읽으면 된다.
- **3초마다 재배치:** 코드가 상자를 출발 상태로 되돌린다. 튀어 오르는 현상이 아니다.

낙하 중 위치를 직접 낮추지는 않는다. 중력과 접촉을 설정하면 물리 엔진이 다음 위치·속도를 계산한다.

## 3. 관절과 구동 — 수레의 위치 제어

[참고용 완성본](C:/makerobot/scripts/02_cartpole_joint.py) · **직접 입력 실습으로 진행, 실행 결과는 아직 미확인**

채팅으로 받은 **관절 위치 제어 전체 코드**를 `C:\makerobot\scripts\02_joint_practice.py`에 그대로 입력한다. 수레·막대가 보이고 `slider_to_cart`, `cart_to_pole` 관절 이름이 출력되는지, 목표가 바뀌면 수레가 움직이는지 확인한다.

```bat
isaaclab.bat -p C:\makerobot\scripts\02_joint_practice.py
```

**목표 위치와 실제 위치의 차이를 관찰한다.** Cartpole은 레일 위 수레에 회전 가능한 막대가 연결된 모델이다.

| 개념 | 이번 실습에서의 의미 |
|---|---|
| 링크 | 수레·막대처럼 로봇을 이루는 단단한 부품 |
| 관절 | 부품 사이의 연결. 수레는 직선 이동, 막대는 회전 가능 |
| 구동기 | 관절을 움직이는 힘·토크를 내는 장치 또는 모델 |

전체 코드를 실행하면 수레의 목표가 가상 시간 3초마다 **`0 → +0.5 → -0.5 → 0m`**로 반복한다.

관찰할 것:

1. `target`은 목표, `cart`는 실제 위치, `error`는 **목표−실제**다. 목표 변경 뒤 오차가 줄어드는지 본다.
2. 목표를 주면 구동기가 힘을 내어 이동한다. 현재 위치를 즉시 덮어쓰는 것과 다르다.
3. 막대에는 구동 토크를 주지 않아 넘어지거나 흔들릴 수 있다. 구동하지 않는 것과 고정하는 것은 다르다.

수레 관절의 위치 단위는 m, 막대 관절의 각도 단위는 rad다. `π rad = 180도`이며 출력의 `pole`만 도(deg)로 변환했다. `v`는 수레 속도(m/s)다.

이번 제어기는 위치 오차를 줄이는 힘과 속도를 억제하는 힘을 계산한다(PD 제어). `stiffness`는 위치 오차에 반응하는 세기, `damping`은 속도를 억제하는 세기다. 강화학습은 아직 하지 않는다.

코드 흐름: **목표 설정 → 명령 전달 → 물리 계산 → 상태 읽기**.

가상 시간 약 10초를 관찰하고, 목표가 바뀌는 3~4.5초의 출력과 수레가 움직였는지를 확인한다.

참고: [Isaac Lab 공식 관절 튜토리얼](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/tutorials/01_assets/run_articulation.html). 제공된 모델에 이번 실습의 위치 제어를 설정했다.

## 4. 공식 튜토리얼 찾아보기

현재 설치 버전에 맞춰 **Isaac Lab 2.3.2 / Isaac Sim 5.1** 문서를 본다. Lab의 아래 튜토리얼은 전체 코드·코드 해설·실행 방법을 함께 제공한다.

먼저 [Lab 빠른 시작 가이드](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/quickstart.html)를 읽어 학습 실행·환경·설정·로봇의 관계를 훑는다. 설치는 이미 완료했으므로 설치 명령을 반복하지 않고, 클라우드 실행과 새 프로젝트 생성은 현재 단계에서 생략한다. 가이드의 학습 명령은 `skrl` 예제이므로 현재 설치·검증한 `RSL-RL`에 맞춰 별도로 안내받아 실행한다. 아래 링크는 참고용이며, 현재 학습 순서는 사용자 정정을 반영한 6장을 따른다.

| 순서 | 공식 문서 | 연결되는 내용 |
|---|---|---|
| 1 | [빈 장면 생성](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/tutorials/00_sim/create_empty.html) | 이미 실행한 시뮬레이션 기본 구조 |
| 2 | [강체 다루기](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/tutorials/01_assets/run_rigid_object.html) | 낙하 실습과 연결되는 물체 생성·상태 읽기 |
| 3 | [관절이 있는 모델 다루기](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/tutorials/01_assets/run_articulation.html) | 현재 Cartpole 실습과 연결되는 관절 상태·명령 |
| 이후 | [강화학습 에이전트로 훈련하기](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/tutorials/03_envs/run_rl_training.html) | 환경 구성 다음의 학습 실행 |

[Isaac Sim 5.1 Quick Tutorials](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/introduction/quickstart_index.html)는 화면 조작과 장면·로봇 구성을 익힐 때 참고한다. 보행 학습 목표에는 Lab 문서를 주교재로 삼는 것을 추천한다.

현재 낙하·관절 실습은 공식 개념을 바탕으로 수정한 보조 예제다. 공식 관절 예제는 두 Cartpole에 무작위 힘을 주고, 우리 예제는 수레 하나가 위치 목표를 따라가게 한다. 원문과 코드·동작이 동일하지 않다.

## 5. Isaac Lab 2.3.2를 선택한 이유

2026-10-05 확인. 첫 프로젝트에서 **설치 조합·코드·문서 버전을 맞추고 환경 변경을 줄이기 위한 선택**이다.

- **호환 조합:** Lab 2.3 계열은 현재 사용 중인 Sim 5.1을 지원한다. 2.3.2는 2.3 계열의 수정·개선을 포함한 릴리스다. [호환표](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/README.md#isaac-sim-version-dependency) · [2.3.2 출시 기록](https://github.com/isaac-sim/IsaacLab/releases/tag/v2.3.2)
- **버전 전환 범위:** 현재 3.0은 Early Access(조기 공개)로 안내된다. Python 3.12와 Sim 6.1 기반이며 설치 방식과 API에 큰 변경이 있다. 기존 환경을 그대로 업그레이드하지 말고 새 환경을 쓰도록 안내한다. Sim 없이 실행하는 경로도 있으므로 모든 3.0 사용에 Sim 6.1이 필수라는 뜻은 아니다. [3.0 출시 기록](https://github.com/isaac-sim/IsaacLab/releases#v3.0.0-EA)
- **현재 유지 이유:** 이 PC에서 2.3.2 조합의 GUI·GPU 최소 예제와 낙하 실습을 확인했다. 보행 학습은 아직 미검증이다. 현재 목적에 필요한 제어·학습 예제가 있으므로 우선 이 환경으로 진행한다.

2.3.2가 RTX 5070에서 가장 빠르다는 비교 결과는 없다. 현재 선택은 호환성과 재현성을 위한 판단이며, 필요한 기능이나 해결할 오류가 생기면 버전 전환을 검토한다.

## 6. Quickstart 자체를 처음부터 따라가기

2026-10-05 사용자 정정: 관절 실습은 아직 하지 않았다. 이전 실습 진도와 무관하게 [제공한 Quickstart 2.3.2](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/quickstart.html)를 처음부터 배우려는 요청이다. 앞서 제안한 Cartpole·RSL-RL 중심 과정과 `03_quickstart_env.py`는 현재 진행 과제에서 제외한다.

원문을 기준으로 도입 → 로컬 설치 → 클라우드 대안 소개 → Ant·skrl 학습 실행 → 환경 목록 → 새 프로젝트 생성 → 설정 → 로봇 구성 → 앱·시뮬레이션 구조 순으로 안내한다. Python 문법보다 각 도구의 역할과 물리적 의미를 설명한다. 코드 작성 실습은 전체 코드를 한 번에 제공하고 사용자의 실행 결과를 확인한다. 원문 예제나 순서를 바꿔야 한다면 이유를 먼저 설명한다.

도입의 핵심:

- Isaac Sim은 물리 계산과 장면 표시를, Isaac Lab은 로봇 학습 환경 구성을 담당한다. skrl 같은 학습 라이브러리는 경험을 이용해 정책을 갱신한다.
- 정책은 관측에서 행동을 정하는 함수다. 학습에서는 경험과 보상을 이용해 그 함수의 파라미터를 조정한다.
- 벡터화는 같은 실험 환경의 여러 복사본을 함께 실행하는 방식이다. 보통 하나의 정책 학습에 이 경험들을 모아 사용한다.
- 모듈화는 행동 처리·관측·보상 등의 역할을 나누어 교체하거나 재사용하기 쉽게 구성하는 것이다.

첫 설치 항목은 별도 Python 환경을 준비하는 이유부터 설명한다. 원문의 새 환경 생성 명령은 `conda create -n env_isaaclab python=3.11`이다. 기존 설치는 보존하고 중복 생성·설치를 반복하지 않는다. 현재 실행 안내:

```bat
conda activate env_isaaclab
python --version
```

목적: 이번 터미널에서 문서가 요구하는 Python 환경을 선택하고 버전을 확인한다. 성공 기준: `(env_isaaclab)` 표시와 Python 3.11.x 출력. **사용자가 이번 출력이 정상이라고 확인했다.** 정확한 출력 전문은 새로 받지 않았다.

### PyTorch와 GPU 확인

PyTorch는 텐서(다차원 수치 배열) 연산과 신경망 학습을 지원한다. 로봇 정책은 관측값에서 행동을 계산하며, 학습 중에는 그 계산에 쓰는 파라미터를 갱신한다. GPU는 이런 대량의 수치 연산을 처리하고 CUDA는 NVIDIA GPU에서 계산하는 데 쓰는 기술이다.

원문 설치 조합은 `torch==2.7.0`, `torchvision==0.22.0`, CUDA 12.8용 패키지 저장소 `https://download.pytorch.org/whl/cu128`이다. torchvision은 영상 처리용 보조 패키지이며 설치한다고 카메라를 사용하는 것은 아니다. 기존 설치를 유지하고 확인 실습부터 한다.

사용자가 채팅의 전체 코드를 `C:\makerobot\quickstart_torch_check.py`에 저장한 뒤 활성화된 환경에서 실행:

```bat
python C:\makerobot\quickstart_torch_check.py
```

예상: torch `2.7.0+cu128`, torchvision `0.22.0+cu128`, CUDA 빌드 `12.8`, GPU 사용 가능 `True`, 결과 장치 `cuda:0`, 결과 평균 `256.0`. 1로 채운 256×256 행렬의 행렬 곱은 각 원소가 256이다. GPU 인식과 실제 연산을 함께 확인하는 검사이며 로봇 학습 성공을 뜻하지 않는다. **사용자가 확인했다고 보고했다.** 이번 출력 전문은 별도로 받지 않았다.

### Isaac Sim 설치와 실행 확인

Isaac Sim은 중력·접촉·관절 움직임 등을 계산하고 장면을 표시하는 시뮬레이터다. 설치 자체가 학습을 시작하는 것은 아니다.

원문은 `python -m pip install --upgrade pip`으로 설치 도구를 갱신한 뒤 `python -m pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com`으로 설치한다. 현재는 설명용 명령이며, 기존 설치를 다시 갱신하거나 설치하지 않는다.

- `all`: Isaac Sim의 주요 Python 패키지 전체 묶음.
- `extscache`: 실행에 필요한 Omniverse 확장 기능 의존성을 캐시한 패키지 묶음. 로봇 모델 전체를 미리 받는 옵션은 아니다.
- `--extra-index-url`: 기본 저장소에 NVIDIA 패키지 저장소를 추가한다.

활성화된 Anaconda Prompt에서 `python -m pip show isaacsim` 실행. 예상은 버전 `5.1.0.0`과 `env_isaaclab\Lib\site-packages` 설치 위치다. 이 결과는 메타패키지 설치 정보이며 전체 실행 정상 여부와 구분한다. 버전이 맞으면 `isaacsim`으로 앱을 열어 편집 화면이 나타나고 메뉴·화면 조작이 가능한지 확인한 뒤 닫는다. **사용자가 버전 일치와 창 정상 실행을 확인했다.**

참고: [Isaac Sim 5.1 Python 설치](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_python.html).

### Isaac Lab 소스와 패키지 설치

`git clone`은 소스 코드를 내려받고, `isaaclab.bat --install`은 저장소의 Python 패키지와 학습 라이브러리를 설치한다. 소스 폴더가 존재하는 것만으로 패키지가 설치된 것은 아니다. Windows의 `.bat`는 이 작업을 묶어 둔 명령 파일이다. 로컬 v2.3.2 스크립트는 소스 패키지를 editable 방식으로 설치하므로 설치 정보가 해당 소스 폴더를 가리킨다.

원문은 기본 브랜치를 clone하지만, 이 튜토리얼을 새로 설치할 때는 `git clone --branch v2.3.2 https://github.com/isaac-sim/IsaacLab.git`으로 문서 버전을 맞춘다. 현재는 다운로드·설치를 반복하지 않고 다음을 사용자가 확인한다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
git describe --tags --exact-match
python -m pip show isaaclab isaaclab_tasks isaaclab_rl skrl
```

예상: Git 태그 `v2.3.2`, 핵심 `isaaclab` 패키지 버전 `0.54.2`. 저장소 릴리스와 개별 패키지의 버전 번호는 다르다. `source`는 구성 라이브러리와 태스크 정의, `scripts`는 실행할 예제·학습 스크립트를 담는다. `isaaclab_rl`은 학습 라이브러리 연동을 담당하며 `skrl` 자체와 별도 패키지다.

**사용자 출력 확인:** `isaaclab 0.54.2`, `isaaclab_tasks 0.11.12`, `isaaclab_rl 0.4.7`이 env_isaaclab에 설치되어 있고 각각 `C:\makerobot\IsaacLab\source` 아래 소스와 editable로 연결되어 있다. `skrl`은 미설치다. 이번 Git 태그 출력은 받지 않았다.

### 빠진 skrl 추가

현재 학습 스크립트는 skrl 최소 버전 `1.4.3`을 명시한다. 재현 가능한 튜토리얼을 위해 이 버전으로 고정해 추가한다. isaaclab_rl은 연결 코드, skrl은 실제 학습 알고리즘 구현이므로 별도 설치가 필요하다.

```bat
python -m pip install "skrl==1.4.3"
python -c "import skrl; from skrl.utils.runner.torch import Runner; print('skrl:', skrl.__version__); print('PyTorch Runner import: OK')"
git describe --tags --exact-match
```

성공 기준: skrl `1.4.3`, `PyTorch Runner import: OK`, Git 태그 `v2.3.2`. **사용자가 모두 예상대로 출력되었다고 확인했다.** 어시스턴트가 설치하지 않았으며 학습 실행 성공은 이후 별도로 확인한다.

### 클라우드 대안과 첫 Ant 학습

원문의 Isaac Launchable은 브라우저에서 클라우드의 개발 화면·시뮬레이터에 접속하는 대안이다. 로컬 설치와 별도 경로이며 이번에는 준비한 PC에서 계속한다.

`Isaac-Ant-v0`는 단순화한 네 다리 로봇의 이동 학습 과제다. 환경은 관측(몸·관절 상태 등), 행동(관절을 돌리는 힘인 토크 명령), 보상(전진·자세 유지 등), 종료 규칙을 제공한다. skrl은 경험을 모아 정책을 갱신한다. 32개 환경은 별개의 경험을 만들고 하나의 정책을 함께 학습한다.

첫 실행은 전체 학습 과정이 동작하는지 확인하기 위한 짧은 학습이다. 기존 시뮬레이터 창을 닫고 Anaconda Prompt에서:

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p scripts\reinforcement_learning\skrl\train.py --task Isaac-Ant-v0 --num_envs 32 --max_iterations 50 --device cuda:0 --seed 42
```

`-p`는 Python 스크립트 실행, `--task`는 학습 과제 선택, `--num_envs`는 병렬 환경 수, `--max_iterations`는 수집·학습 반복 횟수 제한, `--device`는 계산 장치, `--seed`는 난수 시작값이다. `--headless`를 생략해 창을 표시한다. seed 고정만으로 모든 GPU 실행이 완전히 동일해진다고 보장하지 않는다.

로컬 설정에서 한 반복은 환경별 16스텝을 모은 뒤 학습한다. 따라서 50회는 환경별 총 800스텝이며 진행 표시의 800은 에피소드 수가 아니다. 학습 스크립트와 옵션·로그 경로, 체크포인트 저장 구현을 읽어 확인했으며 실행은 하지 않았다.

예상: 로봇 생성과 움직임, 학습 진행 표시, `Training time: ... seconds` 출력 후 종료, 실행별 폴더와 체크포인트 생성. 이 예제의 이동 학습을 목표 속도 추종 평가까지 끝난 프로젝트 완성으로 취급하지 않는다.

**2026-10-05 실제 결과:** 사용자가 로봇이 보이고 움직였다고 보고했다. 로그는 `800/800`, `Training time: 31.6 seconds`, `Simulation App Shutting Down`으로 정상 종료를 보여 준다. GPU 인터페이스 반복 획득에 관한 성능 경고가 있었지만 이후 학습을 끝까지 완료했다.

어시스턴트의 읽기 전용 확인: 실행 폴더 `C:\makerobot\IsaacLab\logs\skrl\ant\2026-10-05_13-39-05_ppo_torch`, 저장 설정의 환경 수 32·seed 42·rollouts 16·총 800스텝 확인. `checkpoints\agent_800.pt`(706,365바이트)를 포함한 체크포인트와 `best_agent.pt` 존재 확인. 저장 정책의 로딩·재생과 보행 성능은 아직 미검증이다.

**학습 목표 해석:** Ant 보상은 목표 방향으로 전진, 생존·몸의 기울기 유지·목표를 향한 방향 정렬에 점수를 주고, 큰 행동·에너지 소비·관절 한계 접근을 감점한다. 서 있기만 해도 일부 보상은 얻지만 전체 과제는 이동이다. 몸통 높이가 0.31m 아래면 해당 에피소드를 종료한다.

800/800의 100%는 설정한 실행량을 마쳤다는 뜻이며 목표 달성률이 아니다. 이번 제한은 학습 50회였고 환경별 진행한 가상 시간은 약 13.3초다(물리 dt=1/120초, decimation=2). 31.6초는 스크립트가 측정한 학습 실행의 실제 시간이다. 창 종료와 함께 멈춘 것은 정상 종료로 설명되며, 종료 전부터 로봇만 정지한 이유는 이 로그만으로 확정할 수 없다.

### 사용 가능한 환경 목록 확인

목적: `--task`에 넣은 이름이 어떤 환경 구현과 설정으로 연결되는지 확인한다. 환경은 로봇 모델과 관측·행동·보상·종료 규칙을 포함하는 실행 단위다. 공식 스크립트의 `--keyword` 옵션으로 Ant만 조회한다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p scripts\environments\list_envs.py --keyword Ant
```

스크립트는 내부적으로 Isaac Sim을 headless로 시작해 등록 목록을 읽고 종료한다. 창이나 로봇 장면은 표시하지 않으며 학습을 하지 않는다. 초기화 로그 뒤 표가 나오는 것을 기다린다. `--keyword`를 생략하면 전체 목록을 조회한다.

표의 `Task Name`은 실행할 과제 ID, `Entry Point`는 환경 생성에 사용할 클래스, `Config`는 환경 설정 클래스다. `모듈경로:클래스이름` 형식으로 표시된다. 예상되는 Ant 항목:

- `Isaac-Ant-v0`: `isaaclab.envs:ManagerBasedRLEnv`. 보상·관측·행동 등을 담당 구성 요소로 나눈 방식이며 방금 학습한 과제다.
- `Isaac-Ant-Direct-v0`: `isaaclab_tasks.direct.ant.ant_env:AntEnv`. 주요 동작을 환경 클래스에 직접 구현한 방식이다.

두 이름은 서로 다른 환경 ID이며 Direct는 학습 난이도나 학습 여부를 뜻하지 않는다. 관측·행동 정의가 다를 수 있으므로 저장한 정책을 다른 ID에 그대로 적용할 수 있다고 가정하지 않는다. **사용자가 두 Ant 행을 공유했고 이름·환경 클래스·설정 경로가 로컬 등록과 일치함을 확인했다.**

### 새 프로젝트 생성 — 흐름 익히기

지금 Quickstart의 목표는 명령·경로 암기보다 과제 선택 → 환경·설정 연결 → 학습·저장의 흐름을 파악하는 것이다. 이후 설정 하나를 바꾸고 결과를 예상·비교하면서 직접 수정할 수 있는 이해로 이어간다.

이번에는 기본 구조 생성 → editable 설치 → 새 과제 등록 확인까지 진행한다. 공식 생성기를 사용자가 실행하며 어시스턴트가 파일을 미리 만들지 않는다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat --new
```

이 명령은 메뉴·템플릿 생성에 필요한 보조 패키지를 설치한 뒤 질문을 표시한다. 선택값: Task type `External`, Project path `C:\makerobot`, Project name `quickstart_lab`, workflow `Direct | single-agent`만, RL library `skrl`만, algorithm `PPO`만. 방향키로 이동하고 복수 선택은 Space로 체크한 뒤 Enter로 확정한다. Project path는 부모 폴더이며 최종 폴더는 `C:\makerobot\quickstart_lab`이다. single-agent는 환경당 제어 주체가 하나라는 뜻이며 병렬 환경 수와 별개다.

생성 완료 후 같은 활성 환경에서:

```bat
cd /d C:\makerobot\quickstart_lab
python -m pip install -e source\quickstart_lab
python scripts\list_envs.py
```

생성기는 Cartpole(레일 위 수레와 회전 가능한 막대) 예제 환경·설정·학습 스크립트·등록 코드를 만든다. `gym.register`는 과제 ID와 환경·설정의 연결 정보를 등록한다. editable 설치 후 새 프로젝트의 목록 스크립트가 해당 패키지를 불러와 등록을 수행한다. 이 단계는 이전 관절 실습 경험을 요구하지 않는다.

성공 기준: 목록에 `Template-Quickstart-Lab-Direct-v0` 표시. 읽기 전용 조회로 `quickstart_lab` 프로젝트 파일·해당 ID의 등록 코드·가상환경 내 설치 메타데이터를 확인했다. 목록 조회의 실제 출력은 아직 받지 않았다.

### 설정: 환경 개수 하나를 바꿔보기

명령을 외우는 것이 첫 순회의 목표는 아니다. 다만 실행 성공만으로 이해했다고 판단하지 않고, 작은 변경을 예상·관찰한 뒤 자기 말로 설명해 본다.

설정 파일: `C:\makerobot\quickstart_lab\source\quickstart_lab\quickstart_lab\tasks\direct\quickstart_lab\quickstart_lab_env_cfg.py`. `scene`의 `num_envs=4096`은 동시에 실행할 환경 개수의 기본값이다. 여기서는 수레와 막대 한 세트가 환경 하나다. `--num_envs`는 이번 실행에 사용할 값을 덮어쓰며 파일 자체를 수정하지 않는다.

Anaconda Prompt에서 실행한다. 첫 창을 닫고 두 번째 명령을 실행한다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\quickstart_lab
python scripts\zero_agent.py --task Template-Quickstart-Lab-Direct-v0 --num_envs 1
python scripts\zero_agent.py --task Template-Quickstart-Lab-Direct-v0 --num_envs 4
```

`zero_agent.py`는 항상 0인 행동을 보내며 학습하지 않는다. 이 Cartpole에서는 수레에 가하는 제어 힘이 0이라는 뜻이다. 중력과 수레·막대 사이의 물리적 상호작용 때문에 움직일 수 있고, 종료 조건에 도달하면 초기화된다. 예상 결과는 같은 과제의 환경 개수가 1개에서 4개로 바뀌는 것이다.

**실제 관찰(2026-10-05):** 사용자가 실험 공간 개수를 바꿨고 화면에서 테스트되는 수레 개수가 달라졌다고 설명했다. 환경 개수 설정과 화면의 세트 개수 변화를 연결해 확인했다. 이 답변만으로 학습 과정 전체의 이해를 판단하지 않는다.

### 설정: 관측과 행동, 0 입력과 무작위 입력

Quickstart Configurations에 나온 `observation_space=4`, `action_space=1`, `action_scale=100.0`을 생성된 Cartpole 코드와 연결하는 보조 실습이다. 관측은 제어에 제공되는 현재 상태 정보이며 이 예제는 막대 각도(rad), 막대 각속도(rad/s), 수레 위치(m), 수레 속도(m/s) 순서로 네 값을 반환한다. 행동은 수레에 줄 힘을 정하는 숫자 하나다. 수레 힘은 `행동 × 100 N`이므로 행동 0.5는 +50 N이다. 환경 개수와 환경 하나의 관측·행동 개수는 다른 설정이다.

상태 네 값은 **막대가 얼마나 기울었는지·어느 방향으로 얼마나 빨리 회전하는지·수레가 어디 있는지·어느 방향으로 얼마나 빨리 이동하는지**를 나타낸다. 같은 기울기라도 더 넘어가는 중인지 바로 서는 중인지에 따라 필요한 힘이 달라져 속도도 관측한다. 정책은 이 네 값을 입력받아 수레 구동기가 가할 힘을 정하는 행동 하나를 출력한다. 네 상태를 각각 별도 구동기로 제어한다는 뜻은 아니다.

`zero_agent.py`는 항상 0을, `random_agent.py`는 매 제어 단계마다 -1~1 범위에서 무작위로 뽑은 값을 보낸다. 둘 다 학습하지 않으며 random agent는 관측에 맞춰 균형을 잡도록 행동을 선택하지 않는다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\quickstart_lab
python scripts\random_agent.py --task Template-Quickstart-Lab-Direct-v0 --num_envs 4
```

예상: 수레에 양·음 방향의 제어 힘이 불규칙하게 가해진다. 매번 같은 움직임이나 더 큰 이동을 보장하지 않으며 넘어짐·범위 이탈·시간 제한 때 초기화될 수 있다.

실제 관찰(2026-10-05): 사용자는 수레가 밀리는 쪽으로 기울어진 막대가 빨리 재시작하고, 다른 막대는 조금 더 버텼다고 보고했다. 환경마다 재시작까지 걸리는 시간이 달랐다는 관찰로 기록한다. 힘은 계속 무작위로 바뀌고 초기 각도·현재 속도도 다르므로, 이 관찰만으로 기울기와 힘 방향의 일반적인 인과관계를 확정하지 않는다. 화면의 이동 방향이 그 순간 가한 힘의 방향과 같다고 단정할 수도 없다. 각 재시작이 어떤 종료 조건 때문이었는지는 미확인이다. 이후 원문 Robots 항목으로 이어간다.

### Cartpole의 종료와 자동 재시작

현재 생성된 코드에서 다음 중 하나면 해당 환경의 한 시도(에피소드)를 끝내고 즉시 초기화한다: **수레 위치의 절댓값 > 3m**, **막대가 위로 선 자세에서 기운 각도의 절댓값 > 90도**, **가상 시간 약 5초 도달**. 프로그램 종료가 아니며 여러 환경은 각자 판정한다.

초기화 때 수레는 기준 위치로 돌아가고 관절 속도는 0이 되며, 막대는 -45~+45도 사이에서 무작위 각도로 재배치된다. 설정의 `initial_pole_angle_range=[-0.25, 0.25]`에 코드가 π를 곱하므로 실제 범위는 ±π/4 rad다. 순간적으로 자세가 바뀌는 것은 학습한 회복 동작이 아니다. 코드로 확인한 규칙이며 현재 사용자의 화면에서 어느 조건이 발생했는지는 미확인이다.

### 강화학습은 무엇을 수정하는가

숫자야구처럼 결과의 피드백을 받아 선택을 개선한다는 비유는 유용하다. 다만 Cartpole에서는 고정된 정답이나 힘 하나를 찾는 것이 아니라, **상태 네 값 → 힘을 정하는 행동 하나**로 연결하는 정책(신경망)의 파라미터를 수정한다.

흐름은 **현재 상태 관측 → 행동 선택 → 물리 계산 → 보상·다음 상태 수집 → 모은 경험으로 정책 갱신**이다. PPO 같은 방법은 예상보다 좋은 결과로 이어진 행동을 비슷한 상태에서 더 선택하도록 조정하는 방향으로 학습한다. 한 행동 직후의 보상뿐 아니라 이후 보상도 고려한다. Cartpole의 보상에는 생존과 함께 기울기·속도·실패에 관한 항목도 있으므로 버틴 시간만 최적화하는 것은 아니다. 탐색과 추정 오차 때문에 매번 성능이 좋아지는 것은 아니다. 이는 학습 원리 설명이며 Cartpole 학습 실행·성공을 확인한 기록은 아니다.

### Robots: 로봇 설정과 환경 설정의 연결

원문 Robots는 Dofbot으로 로봇 설정을 설명한다. 같은 구조를 현재 실행한 Cartpole에 대응해 읽는다. 환경 설정 `C:\makerobot\quickstart_lab\source\quickstart_lab\quickstart_lab\tasks\direct\quickstart_lab\quickstart_lab_env_cfg.py`는 `CARTPOLE_CFG`를 불러와 `robot_cfg`로 사용한다. `.replace(prim_path=...)`는 설정을 복사하면서 시뮬레이션 장면의 배치 경로를 지정한다. 이는 USD 파일의 디스크 경로와 다르다.

실제로 읽을 로봇 설정 파일은 `C:\makerobot\IsaacLab\source\isaaclab_assets\isaaclab_assets\robots\cartpole.py`다. `ArticulationCfg`는 관절로 연결된 물체의 설정이다. `spawn`은 USD 모델을 불러오고 물리 속성을 지정하며, `init_state`는 기본 시작 위치·관절 상태, `actuators`는 관절에 힘/토크를 가하는 구동 모델의 설정이다. USD에는 형상뿐 아니라 물리·관절 정보도 담길 수 있다.

`slider_to_cart`는 수레의 직선 이동 관절, `cart_to_pole`은 수레와 막대 사이 회전 관절이다. 이 과제의 행동은 수레 관절에 힘을 지정한다. 막대는 직접 제어 토크를 받지 않으며 수레 운동·중력에 반응한다. `pole_actuator`라는 설정 이름이 있어도 이 과제가 막대를 직접 구동한다는 뜻은 아니다. 기본 관절 위치 0과 과제 리셋 시 무작위 막대 각도는 별개로, 실제 시작 상태에는 리셋 코드가 적용된다.

사용자는 직접 힘을 주는 대상이 수레라고 답했고, 막대의 `damping=0`을 그 이유로 추측했다. 대상은 맞지만 근거를 구분해 설명했다. 행동의 전달 대상은 환경 코드 `_apply_action()`의 `joint_ids=self._cart_dof_idx`가 정한다. `damping`은 목표 속도와 현재 속도의 차이에 비례하는 힘/토크의 계수이며, 목표 속도가 0일 때 운동을 억제하는 방향으로 작용한다. `damping=0`이어도 별도로 힘/토크 명령을 보낼 수 있다. 현재 막대에는 행동 토크를 보내지 않고 stiffness·damping도 0이다.

앞선 `행동 × 100 N`은 행동에서 지정한 힘을 뜻한다. 수레에는 `damping=10`도 있으므로 구동기가 가하는 전체 힘이나 물체에 작용하는 모든 힘의 합과 같다고 해석하지 않는다. 설명 후 이해 확인은 아직 미확인. 이후 원문의 Apps and Sims로 이어간다.

### 수레의 힘 명령과 감쇠

현재 Cartpole 수레 구동 모델은 `stiffness=0`, `damping=10`이다. 힘 명령 외에 속도 목표 0을 향하는 감쇠 작용이 있어, 움직이는 방향의 반대로 힘을 낸다. 연속시간의 단순화한 관계는 `감쇠력 = -10 × 수레 속도`(속도 m/s, 힘 N)다. 예를 들어 오른쪽 속도 1m/s일 때 힘 명령이 0이어도 왼쪽 감쇠력 약 10N이 작용하는 것으로 이해한다. 실제 시뮬레이션의 이산 계산과 막대의 상호작용 등은 별도다.

따라서 **행동 0은 추가 힘 명령이 0이라는 뜻이며, 구동 모델의 모든 힘 또는 수레에 작용하는 힘의 합이 0이라는 뜻은 아니다.** 앞선 '구동기가 힘을 내지 않는다'는 설명은 감쇠가 있는 이 수레에 대해서는 이처럼 구분해야 한다. 감쇠는 시뮬레이션에 설정된 속도 억제 작용이며 학습으로 생긴 행동이 아니다.

### Apps and Sims: 시작과 시간 진행 구분하기

Quickstart 마지막 항목. `AppLauncher(args)`는 Isaac Sim 앱을 시작한다. 앱 시작 이후에 불러와야 하는 시뮬레이션 모듈이 있으므로 import 순서를 유지한다. 현재 RL 환경에서는 `gym.make()`로 과제를 만들고, `env.reset()`으로 시작 상태를 준비한 뒤 `env.step(actions)`로 행동 적용·물리 계산·보상/종료 판정·관측 갱신을 수행한다. `simulation_app.is_running()`은 앱 실행 여부를 확인하고, `close()`는 정리한다. 별도 Standalone 시뮬레이션에서는 물리 계산과 상태 갱신을 직접 관리할 수 있지만 이번에는 기존 환경의 step을 사용한다.

사용자가 작성할 완결된 보조 실습 `C:\makerobot\quickstart_lab\quickstart_app_steps.py`의 전체 코드를 채팅으로 안내했다. Cartpole 1개에 0 행동을 보내며 180번 진행하고, 60번마다 누적 가상 시간을 출력한 뒤 자동 종료한다. 행동에서 지정하는 추가 힘이 0이어도 중력·감쇠 등은 작용한다. 현재 `dt=1/120초`, `decimation=2`이므로 환경 step 한 번은 물리 계산 두 번, 가상 시간 1/60초다. 예상 출력은 60·120·180 step에서 1·2·3초이며 PC 처리 시간이나 화면 FPS와 구분한다. 에피소드가 초기화되어도 이 출력은 전체 실행의 누적 시간이다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\quickstart_lab
python quickstart_app_steps.py
```

실제 결과(2026-10-05): 사용자가 화면에서 약 5번의 환경 재시작을 관찰했고 `step=180` 출력을 보고했다. 앞서 창이 뜨지 않고 `omni.kit.viewport.window` 초기화 부근에서 기다리는 상태를 확인해 Esc 확인을 안내했지만, 실제로 진행이 재개된 원인은 보고되지 않았다. 화면 실행과 180 step 도달은 확인됐으며 자동 종료 여부는 명시적으로 확인되지 않았다.

스텝은 `env.step()`으로 행동을 적용하고 시간을 한 단계 진행하는 단위다. 에피소드는 초기 상태에서 시작해 종료 조건에 도달하기까지의 한 시도이며 여러 스텝으로 구성된다. 종료 후 해당 환경을 리셋해 다음 에피소드를 시작한다. 이 실습의 출력 `step`은 바깥 for문의 전체 누적 횟수이므로 환경이 리셋되어도 1로 돌아가지 않는다. 총 180 step(가상 시간 3초) 안에 여러 짧은 에피소드가 포함될 수 있다. 약 5회라는 관찰은 정확한 종료 횟수 로그가 아니며 각 종료 원인은 미확인이다. 다음은 앞서 저장한 Ant 정책 재생으로 학습·저장·재실행 흐름을 연결한다.

### 저장한 Ant 정책 다시 실행하기

사용자는 step을 가상 시간을 나눈 단위이며 매번 행동을 적용하는 것으로 설명했다. 환경 step은 행동을 받아 시뮬레이션을 한 번 진행하는 단위이고, 대응하는 시간은 설정에 따라 달라진다. 행동은 매번 전달하지만 값이 매번 달라질 필요는 없다. 사용자의 요청으로 매 실습 끝 빈칸·예측 문제 1~2개를 지속하기로 했다.

Quickstart 원문을 한 차례 살펴본 뒤, 앞서 학습한 Ant 체크포인트를 공식 skrl `play.py`로 불러오는 연결 실습이다. 정책은 현재 관측에서 행동을 정하는 학습된 함수이며, 체크포인트에는 이를 다시 불러올 모델 상태 등이 저장된다. 재생은 저장 동작 영상을 틀거나 추가 학습하는 과정이 아니라, 새 시뮬레이션의 현재 관측으로 행동을 계산하는 추론이다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Ant-v0 --num_envs 4 --checkpoint "C:\makerobot\IsaacLab\logs\skrl\ant\2026-10-05_13-39-05_ppo_torch\checkpoints\agent_800.pt" --device cuda:0 --real-time
```

읽기 전용으로 지정한 체크포인트 존재와 play.py 인자를 확인했다. `--real-time`은 가능한 경우 가상 시간과 실제 시간 진행 속도를 맞추며, 계산이 느리면 더 느릴 수 있다. 학습 때의 32환경에서 재생 4환경으로 줄여도 같은 정책을 각 환경에 적용한다. 실제 결과(2026-10-05): 사용자가 실행 성공과 몸을 움직이다 멈추는 주기적 반복을 보고했다. 저장 정책 로딩·실행 흐름을 경험했으나 보행 성능은 미평가다.

복습 답변: ① 3초 정답. 전체 누적 step이 계속 증가한다는 빈칸은 미응답으로 보충 설명. ② 관측·행동·갱신하지 않는다 정답. 다만 사용자는 현재 관측을 넣는 것을 학습 당시 장면 재현으로 이해해 추가 설명했다.

정책은 과거 관측·행동을 시간순으로 재생하지 않는다. 저장된 신경망 파라미터를 사용해 **현재 관측 → 행동 → 물리 계산 → 다음 관측**을 반복한다. 학습보다 오래 실행해도 데이터가 소진되는 일이 없다. 학습 때 만나지 못한 상태에도 입력 형식이 같으면 행동을 계산하지만, 유효한 제어가 된다는 보장은 없다. 학습 경험 밖의 상태에 대응하는 능력을 일반화라고 하며, play 중 실패해도 정책 파라미터는 자동 개선되지 않는다.

로컬 Ant 설정은 한 에피소드 최대 가상 시간 16초, 몸통 높이 0.31m 미만이면 조기 종료·리셋하도록 되어 있다. 사용자가 반복 중 처음 자세로 돌아온다고 확인하여 환경 리셋이 포함된 것으로 해석한다. 어느 종료 조건이 발생했는지와 에피소드 안에서 움직임이 멈추는 원인은 미확인이다.

추가 복습 답변: ① 계산할 수 있다·보장되지 않는다, ② 갱신되지 않는다 모두 정답. 이어 사용자가 현재 정책은 학습하지 않은 것이므로 무작위 행동과 같다고 추측하여, 과거 학습 이력과 현재 실행 모드를 구분해 설명했다.

이번 `agent_800.pt`는 앞서 train.py를 32환경·800 step으로 실행한 뒤 저장한 체크포인트다. play.py는 이미 학습한 파라미터를 불러와 사용하며 추가 갱신을 하지 않는다. 짧은 학습 뒤 잘 걷지 못한다고 미학습·무작위 행동과 동일한 것은 아니며 무작위 대비 성능 우열은 평가 전 미확정이다. 환경 리셋은 로봇 상태를 초기화하고 학습된 정책 파라미터는 유지한다. 다음 실습은 학습량을 늘린 정책과 현재 정책 비교를 계획하되, 먼저 이 구분을 복습한다. 복습(미응답): 현재 정책은 이전에 ___했고, play 중에는 추가로 ___하지 않는다. 환경이 리셋되면 정책 파라미터는 유지된다/처음부터 무작위로 바뀐다.

### Ant 학습량을 늘려 비교하기

사용자가 이전 정책의 학습 이력과 리셋 시 정책 유지에 대해 ‘학습’, ‘유지된다’로 답했다. play 중에는 추가 학습하지 않는다는 전체 문장을 보충한 뒤 비교 실습으로 진행한다.

이전 학습의 과제·32환경·seed 42·GPU·GUI 조건을 유지하고 `max_iterations`를 50→1000으로 늘린다. 체크포인트를 지정하지 않으므로 새 정책을 초기화해 처음부터 학습하며, 예전 pt에서 이어 학습하는 명령은 아니다. 날짜·시간으로 구분된 새 로그 폴더에 저장되어 기존 결과와 비교할 수 있다. seed는 난수 생성의 기준값이며 같은 값만으로 완전한 재현성을 보장하지 않는다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p scripts\reinforcement_learning\skrl\train.py --task Isaac-Ant-v0 --num_envs 32 --max_iterations 1000 --device cuda:0 --seed 42
```

현재 skrl 설정은 rollouts=16이며 스크립트가 timesteps=max_iterations×rollouts로 정한다. 예상 진행률 끝은 16000/16000(기존 800의 20배). 환경 개수 32는 별도다. 앞선 학습 31.6초의 단순 20배는 약 10분이나 실제 소요 시간은 달라질 수 있다. 학습량 증가가 보행 성공을 보장하지 않으며 완료 후 저장 파일을 확인해 동일한 재생 조건으로 비교한다. 사용자는 기존 재생 창을 닫고 실행하며 학습 중에는 창을 닫지 않는다. 실제 결과(2026-10-05): 사용자 로그로 16000/16000 완료, Training time 550.05초(약 9분 10초)를 확인했다. 새 실행 폴더는 `logs\skrl\ant\2026-10-05_16-47-58_ppo_torch`이며, 읽기 전용 조회로 `checkpoints\agent_16000.pt` 저장과 seed 42·32환경·rollouts 16·timesteps 16000을 확인했다. 보행 성능 변화는 아직 미평가다.

이번 복습 답변: ① 유지된다, ② X 모두 정답. 사용자는 학습량 증가가 최선의 행동 탐색을 보장하지 않으며 조건을 바꾼 시행착오가 필요하다고 설명했다. 비교할 때는 한 번에 한 조건만 바꾼다. seed 변경은 난수에 따른 결과 편차를 확인하는 수단이며 잘못된 보상 설계 자체를 고치는 방법은 아니다. 현재는 같은 로봇에서 학습량에 따른 차이부터 관찰한다.

### Ant가 배우는 목표와 긴 학습 결과 재생

현재 Ant 과제는 네 다리로 몸통의 정상 자세를 유지하면서 목표 방향으로 전진하도록 학습한다. 로컬 `ant_env_cfg.py`와 보상 함수에서 목표점 방향으로 가까워지는 진행량, 생존, 몸통의 위쪽 정렬과 목표 방향 정렬에 양의 보상을 주고, 큰 행동·에너지 사용·관절 한계 접근에는 감점을 주는 것을 확인했다. 보상은 각 행동의 결과를 평가하는 점수이며 정책은 앞으로 받을 보상의 합을 높이는 방향으로 학습된다. 특정 걸음 순서를 지정하거나 목표 속도 1m/s를 추종시키는 과제는 아니다. 제자리에 서 있어도 일부 점수를 받을 수 있지만 전진에 대한 보상은 얻지 못한다.

새 정책을 기존과 같은 4환경·실시간 재생 조건으로 비교했다. 사용자 관찰: 일부는 움직이다 멈췄고, 일부는 몸통을 유지하며 이전보다 더 오래 전진했다. 재생 실행과 일부 개선된 움직임은 확인됐지만 평균 성능·안정성 향상은 아직 정량 검증하지 않았다.

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Ant-v0 --num_envs 4 --checkpoint "C:\makerobot\IsaacLab\logs\skrl\ant\2026-10-05_16-47-58_ppo_torch\checkpoints\agent_16000.pt" --device cuda:0 --real-time
```

관찰할 것은 이전보다 전진이 지속되는지와 몸통을 유지하는지다. 최대 에피소드 길이가 가상 시간 16초라 잘 움직여도 시간 제한으로 리셋될 수 있다. 몸통 높이 0.31m 미만인 경우도 종료되므로 리셋만으로 넘어짐을 단정하지 않는다. 복습 두 답 모두 정답: 사용자는 제자리 버티기로는 전진 보상을 얻지 못하며, 시간 제한 리셋일 수도 있어 리셋만으로 실패를 단정할 수 없다고 설명했다. 새 정책의 실제 움직임 비교 결과는 위에 기록했다.

사용자는 일정 시간 움직이지 않으면 감점을 주는 방안을 제안했다. 가능한 보상 설계이지만 필수 수정은 아니다. 현재도 전진 보상이 있으며 정지는 보상 간 비중이나 아직 이동 방법을 배우지 못한 상태 등 여러 원인으로 나타날 수 있다. 원인은 현재 미확인이다. 단순히 다리가 움직이는지만 기준으로 삼으면 제자리에서 다리만 흔드는 행동도 감점을 피할 수 있으므로, 실제 목표인 몸통의 목표 방향 진행량과 연결해 설계해야 한다. 먼저 학습량만 바꾼 두 정책의 관찰 결과를 확인하고 보상 변경 여부를 판단한다. 보상 설정은 수정하지 않았다.

추가 예측 답변: 사용자는 제자리 점프 또는 주기적인 작은 몸 위치 변경으로 감점을 피할 수 있다고 설명했다. 전진 없이도 규칙을 만족할 수 있다는 취지는 맞다. 작은 움직임의 면제 여부는 움직임의 측정 대상·최소 크기·시간 기준에 달려 있다. 실제로 이런 행동을 학습했다는 관찰은 아니다.

### 다음 평가에서 무엇을 셀 것인가

다음은 두 저장 정책을 같은 환경 수·평가 seed·에피소드 수·최대 길이로 실행해 비교할 계획이다. 측정할 것은 시작부터 종료까지의 몸통 전진 변위(m), 에피소드 지속 시간(가상 초), 종료 원인(몸통 높이 조건/시간 제한)이다. 평균 전진 속도는 전진 변위÷지속 시간이며, 왕복한 총 이동 거리와 다르다. 시간 제한까지 버틴 것만으로 보행 목표 달성을 단정하지 않는다. 현재 관찰만으로 로봇별로 다른 정책이라고 해석하지 않는다. 같은 정책을 사용하지만 초기 관절 상태 등의 차이로 행동과 결과가 달라질 수 있다.

계산 연습의 가상 예시: A는 16초 동안 0m 전진하고 시간 제한 종료, B는 16초 동안 4m 전진하고 시간 제한 종료, C는 5초 동안 2m 전진하고 몸통 높이 조건으로 종료한다. 실제 측정 결과가 아니다. 복습 답변: 사용자는 0.25m/s로 정확히 계산했고, 속도만으로 좋은 보행을 단정할 수 없으며 목적에 따라 평가의 우선순위가 달라진다고 설명했다. 속도가 항상 부차적이라는 일반화는 보충했다. 이 프로젝트의 첫 완료 기준은 목표 속도 추종과 넘어짐 빈도를 함께 평가하는 것이다. Ant 입문 평가는 아직 목표 속도 추종 검사가 아니다.
### Ant 두 정책의 첫 에피소드 수치 비교

사용자가 `C:\makerobot\quickstart_lab\evaluate_ant.py`에 직접 입력할 완결된 평가 코드를 채팅으로 제공했다. 4환경·seed 42·각 환경 첫 에피소드 1개·최대 가상 시간 16초로 두 체크포인트를 별도 프로세스에서 평가한다. 정책을 추가 학습하거나 덮어쓰지 않는다. 평가 코드는 로컬 v2.3.2/skrl 1.4.3 소스와 Python 구문을 확인했다. 사용자가 파일을 작성해 두 명령을 실행했지만, 설정 파일을 읽은 뒤 RESULT/SUMMARY 없이 종료됐다고 보고했다. 이후 오타 수정 뒤 두 평가의 RESULT/SUMMARY 출력과 종료를 확인했다(아래 실제 결과 참조).

이번 전진량 `dx`는 몸통의 세계 좌표 +X 변위(m), `mean_vx`는 dx÷첫 에피소드 지속 시간(가상 초)이다. 목표점이 먼 +X 쪽에 있으므로 입문용 전진 지표로 사용하며, 목표점까지의 거리 감소량과 완전히 같은 값은 아니다. Recorder의 post-step 시점에서 리셋 직전 위치를 보관한다. env.step 반환 뒤의 로봇 위치만 읽으면 이미 리셋된 시작 위치일 수 있다. 각 환경의 첫 에피소드만 한 번씩 집계하여 빨리 종료하는 환경의 시도가 과도하게 포함되지 않게 한다.

`fall`은 현재 Ant의 몸통 높이 0.31m 미만 종료, `timeout`은 시간 제한, `fall+timeout`은 두 조건 동시 충족이다. SUMMARY는 평균 변위·평균 지속 시간·높이 조건 종료 수/4를 출력한다. 4개 측정이 끝나면 자동 종료하며, 조기 창 종료는 INCOMPLETE로 표시한다. 이 네 번만으로 전체 성능이나 일반화를 확정하지 않는다.

Anaconda Prompt에서 환경 활성화 후 `C:\makerobot\IsaacLab`로 이동하여 아래를 하나씩 실행한다.

```bat
isaaclab.bat -p C:\makerobot\quickstart_lab\evaluate_ant.py --device cuda:0 --checkpoint "C:\makerobot\IsaacLab\logs\skrl\ant\2026-10-05_13-39-05_ppo_torch\checkpoints\agent_800.pt"
isaaclab.bat -p C:\makerobot\quickstart_lab\evaluate_ant.py --device cuda:0 --checkpoint "C:\makerobot\IsaacLab\logs\skrl\ant\2026-10-05_16-47-58_ppo_torch\checkpoints\agent_16000.pt"
```

확인할 결과는 각 실행의 RESULT 4줄과 SUMMARY 1줄이다. 복습 답변: ① 정지 또는 작은 움직임을 의심한다, ② 학습량의 영향을 판단하려는 목적이다. 두 답의 취지는 맞으며, dx≈0이어도 왕복 또는 옆 방향 이동이 가능하고, 조건 통제는 다른 요인의 영향을 줄여 비교하는 것이라고 보충했다. 소수의 시도만으로 통계적 유의성을 확정하지 않는다.

실행 오류 점검(2026-10-05): 사용자 파일을 읽기 전용으로 확인했다. 47행에 `agent_Cffg = load_cfg_from_registry(...)`라고 저장되어 다음 행의 `agent_cfg`가 정의되지 않는다. 로그가 두 설정 로딩 뒤 멈춘 위치와 일치한다. 46행의 `cfg.recorder`도 실제 환경에서 사용하는 `cfg.recorders`로 수정해야 기록기가 등록된다. 두 줄의 올바른 코드를 안내했으며 사용자 파일은 수정하지 않았다. 기존 finally의 app.close()는 오류가 있어도 수행되고 앱 종료가 오류 출력을 가릴 수 있어, 종료 전에 traceback.print_exc()와 출력 flush를 수행하는 마지막 블록을 추가 안내했다. 원래 제공 코드에서 오류를 먼저 출력하도록 하지 않은 점을 보완한다. 먼저 agent_800.pt 한 번을 재실행해 RESULT/SUMMARY 또는 Traceback을 확인한다. 이후 사용자 재실행 결과로 두 평가 완료를 확인했고, 읽기 전용 조회로 두 오타 수정도 확인했다.

### Ant 첫 수치 비교 실제 결과 (2026-10-05)

사용자가 두 실행의 RESULT 4줄·SUMMARY·종료 로그를 제공했다. 앞 출력은 agent_800.pt, 뒤 출력은 agent_16000.pt라는 기존 실행 안내 순서로 해석한다(붙여준 로그에는 EVAL 경로가 생략됨). 평가 파일에서 4환경·seed 42·리셋 직전 위치 기록·첫 에피소드만 집계하는 설정을 읽기 전용으로 재확인했다.

| 학습 step | env | 지속 시간(s) | +X 변위(m) | 평균 vx(m/s) | 종료 |
|---|---:|---:|---:|---:|---|
| 800 | 0 | 16.00 | -0.088 | -0.005 | timeout |
| 800 | 1 | 1.50 | 0.625 | 0.417 | fall |
| 800 | 2 | 16.00 | 0.339 | 0.021 | timeout |
| 800 | 3 | 16.00 | 0.143 | 0.009 | timeout |
| 16000 | 0 | 4.48 | 4.420 | 0.986 | fall |
| 16000 | 1 | 1.50 | 0.406 | 0.271 | fall |
| 16000 | 2 | 16.00 | 19.398 | 1.212 | timeout |
| 16000 | 3 | 16.00 | -0.075 | -0.005 | timeout |

SUMMARY: 800은 mean_dx=0.255m, mean_time=12.38s, falls=1/4. 16000은 mean_dx=6.037m, mean_time=9.50s, falls=2/4. 이번 표본에서 평균 전진량은 증가했으나 높이 조건 종료 수는 늘었다. 16000의 env=2는 16초간 높이 조건 종료 없이 19.398m 전진했고, env=0은 4.48초에 4.420m 전진 후 높이 조건으로 종료했다. env=3은 제한 시간까지 버텼지만 순전진은 거의 없었다. 순변위만으로 정지·왕복·옆 이동을 구분할 수 없다. 평균 변위 6.037m를 모든 시도의 전진량으로 해석하지 않는다.

학습·저장·재실행·첫 수치 비교 흐름은 실행 확인됐다. 이 네 시도의 넘어짐 비율 25%/50%는 표본 비율이며 일반적인 실패 확률이나 학습 증가에 따른 안정성 저하를 확정하지 않는다. 목표 속도 추종과 보행 형태의 적절성은 이 출력으로 평가하지 않았다. GPU 인터페이스 캐시 성능 경고가 출력됐지만 두 실행은 SUMMARY까지 도달했다.

복습 답변: 사용자는 같은 timeout이라도 이동량 관점에서 동일하지 않고, 평균만 보면 잘된 사례에 가려 넘어짐 등 문제를 놓칠 수 있다고 설명했다. 두 답 모두 정답. 이후 어시스턴트가 40회 평가·CSV 저장 코드를 준비했으나, 사용자가 원문 튜토리얼에 필요한 단계인지 질문하여 확장을 중단했다. 해당 코드는 채팅으로 제공하거나 파일로 작성하지 않았고 시뮬레이션도 실행하지 않았다.

### Quickstart 원문 범위 재확인 (2026-10-05)

사용자 질문: 지금 진행이 정말 필요하고 원문 튜토리얼을 따르는 것인지 확인 요청. 공식 v2.3.2 Quickstart를 다시 읽어, 원문은 설치·Launchable 대안·Ant 학습 실행·환경 목록·프로젝트 생성·Configurations·Robots·Apps and Sims로 구성됨을 확인했다. 이 항목들은 대화에서 한 차례 다뤘다. 일부 개념은 원문 예시 대신 Cartpole 보조 실습으로 설명했으며, 원문 항목을 다룬 것과 모든 개념 숙달은 구분한다.

저장 정책 재생은 흐름 이해를 위한 보충이고, 800/16000 학습량 비교·사용자 정의 evaluate_ant.py·40회 평가/CSV는 원문에 없는 확장이다. 앞선 학습량 비교와 4회 평가는 실제 완료했지만, Quickstart를 마치기 위해 추가 40회 평가까지 할 필요는 없다. 장기 프로젝트의 평가 목표를 현재 원문 학습의 필수 조건으로 확대 적용한 것은 어시스턴트의 범위 관리 오류다. 현재 추가 평가는 중단하며, 기존 결과는 보존한다. 다음 안내부터 원문 항목과 이해에 필요한 짧은 보충, 선택 확장을 명확히 구분하고 선택 확장을 당연한 다음 단계로 진행하지 않는다.

원문: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/quickstart.html

## 7. Build your Own Project or Task — Project Structure

2026-10-05 사용자가 장기적으로 필요한 확장이라면 진행해도 되며, 필요성을 판단해 확장 또는 공식 다음 단원으로 진행하도록 위임했다. 반복 평가는 향후 필요하지만 현재 Ant의 추가 40회 평가는 학습 효과보다 반복 부담이 커 우선순위를 낮춘다. 현재는 평가 지표의 한계를 이해하고 두 정책을 수치로 비교하는 단계까지 완료했다. 실제 보행 과제와 성공 기준을 정한 뒤 반복 평가로 돌아간다. 공식 다음 묶음인 Build your Own Project or Task로 이동하며, 이미 수행한 생성·설치를 반복하지 않고 Project Structure를 진행한다.

출처: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/overview/own-project/project_structure.html

목적은 과제 이름이 어떤 환경 코드·환경 설정·학습 설정으로 연결되는지 찾는 것이다. 실제 로컬 파일을 읽기 전용으로 확인했다. 공식 문서의 네 계층을 현재 프로젝트에 대응하면 다음과 같다.

- Project: `C:\makerobot\quickstart_lab` — scripts와 source 등을 묶는 전체 작업 폴더.
- Extension: `C:\makerobot\quickstart_lab\source\quickstart_lab` — setup.py·config/extension.toml을 포함하는 설치 단위.
- Module/package: 그 안의 `quickstart_lab` — Python에서 import하는 코드.
- Task: 패키지 내부 `tasks\direct\quickstart_lab` — 환경 구현·설정·등록·학습 설정이 모인 과제.

`tasks\direct\quickstart_lab\__init__.py`의 gym.register는 id=`Template-Quickstart-Lab-Direct-v0`, entry_point=환경 클래스 QuickstartLabEnv, env_cfg_entry_point=환경 설정 QuickstartLabEnvCfg, skrl_cfg_entry_point=agents/skrl_ppo_cfg.yaml을 연결한다. pip editable 설치는 Python에서 프로젝트 코드를 찾도록 연결하는 단계이고, 실제 Gym 등록은 실행 프로세스가 관련 모듈을 import할 때 일어난다. 로컬 scripts/skrl/train.py에서 import quickstart_lab.tasks 및 gym.make 호출을 확인했다.

quickstart_lab_env_cfg.py는 action_scale=100N·max_cart_pos=3m·보상 계수 등 설정값을 둔다. quickstart_lab_env.py는 _apply_action·_get_observations·_get_rewards·_get_dones·_reset_idx를 통해 그 값을 적용하고 관측·보상·종료 등을 계산한다. agents/skrl_ppo_cfg.yaml은 PPO 신경망 구성·학습률 등 학습 설정이며, 학습 후 저장한 정책 파라미터인 pt 파일과 다르다.

이번 읽기 실습: 해당 Task의 __init__.py에서 등록 ID와 연결 항목을 찾고, env_cfg의 max_cart_pos=3.0이 env.py의 _get_dones에서 self.cfg.max_cart_pos로 사용되는 연결을 찾는다. 파일 편집·설치·시뮬레이션 실행은 필요하지 않다. 완료 기준은 숫자 설정과 그 값을 사용하는 동작 코드의 위치를 구분해 설명하는 것이다. 복습 답변: ① quickstart_lab_env_cfg.py의 max_cart_pos, ② gym.register·entry_point 모두 정답. 설정값과 환경 코드 연결, 과제 등록의 핵심 위치를 구분했다.

## 8. Walkthrough — Environment Design Background

공식 Walkthrough의 첫 단원으로 이동했다. 이 단원은 환경이 행동을 받아 세계를 진행시키고 관측·보상을 반환한다는 배경에 이어 App·Sim·World·Stage·Scene을 설명한다. 사용자에게 익숙한 Cartpole 코드와 대응하며, 아직 Jetbot 프로젝트 생성·로봇 교체·추가 학습은 하지 않는다.

출처: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/walkthrough/concepts_env_design.html

- App: 앱 수명·자원을 관리한다. headless도 앱은 실행되며 화면 창을 표시하지 않는 방식이다.
- Sim: 시간 간격·중력 등 물리 계산과 렌더링 진행을 관리한다.
- World: 위치와 방향·단위를 해석하는 공간 기준이다. 여기서는 별도 World 클래스 인스턴스를 만들라는 뜻이 아니다.
- Stage: USD 객체(prim)의 계층과 배치를 표현한다. /World/envs/env_0/Robot은 디스크 파일 경로가 아니라 시뮬레이션 내부 객체 경로다.
- Scene: 로봇·센서 등 관련 객체를 묶어 여러 환경의 생성·상태 접근을 관리한다. 여러 환경은 같은 앱과 시뮬레이션 안에 함께 존재한다.

로컬 env_cfg에서 SimulationCfg(dt=1/120), robot_cfg의 prim_path=/World/envs/env_.*/Robot, InteractiveSceneCfg(num_envs=4096, env_spacing=4.0)을 확인했다. 실행 인자의 num_envs로 기본 환경 수가 바뀔 수 있다. env.py의 _setup_scene에는 scene.clone_environments와 scene.articulations["robot"] 등록이 있다. env_.*는 여러 환경에 있는 Robot 경로를 가리키는 패턴이다.

좌표 예시(실제 측정 아님): 환경들의 좌표축 방향과 단위가 같고 한 환경의 원점이 세계 X=10m일 때, 그 환경 기준 X=0.5m인 수레의 세계 X는 10.5m다. 따라서 같은 초기 자세라도 환경 원점이 다르면 세계 좌표가 다를 수 있다. 실제 이전 평가의 dx는 시작·종료 세계 X의 차이이므로 고정된 원점 오프셋이 상쇄된다.

이번 읽기 실습은 위 env_cfg의 sim·robot_cfg·scene 세 항목을 용어와 연결한다. 사용자 편집·실행 없이 진행한다. 복습 답변: 사용자는 앱이 아니라 환경이 4개라고 답했고, 수레의 세계 X를 9.5m로 계산했다. 두 답 모두 정답. 이어 세계라는 말이 세계 기준 좌표를 뜻하는지 질문하여, 세계 좌표계는 시뮬레이션 전체의 공통 원점·축 방향·단위이며 세계 좌표는 그 기준으로 표현한 위치라고 구분했다. 같은 수레 위치를 환경 기준 X=-0.5m와 세계 기준 X=9.5m로 각각 표현할 수 있다(축 방향·단위가 같다는 예시 조건).

환경 간 충돌 보충: 현재 Isaac-Ant-v0의 GPU 실행 설정은 InteractiveSceneCfg의 기본 filter_collisions=True를 사용한다. 따라서 서로 다른 환경의 Ant 사이에는 접촉력이 발생하지 않도록 설정되어 있으며, 공통 바닥과의 접촉은 유지된다. num_envs=4 자체가 충돌을 금지하는 것은 아니다. 환경은 각 로봇의 상태·행동·보상·종료를 관리하는 실험 단위이고, env_spacing은 초기 배치 간격이지 벽이나 힘이 적용되는 영역의 경계가 아니다. 세계 좌표를 공유해도 충돌 대상은 따로 설정할 수 있다. 로컬 Ant 설정과 InteractiveScene 구현을 읽어 확인했으며, 로봇을 겹치게 하는 추가 실행은 하지 않았다.

출처: https://isaac-sim.github.io/IsaacLab/v2.3.2/_modules/isaaclab/scene/interactive_scene.html
환경 충돌 복습 답변: 사용자는 X로 정답을 골랐다. 다만 “환경 안의 요소들끼리 간섭 불가능”은 너무 넓으므로, 현재 설정에서 서로 다른 환경 물체 사이의 충돌력이 차단된다는 의미로 한정했다. 같은 환경의 물체와 공통 바닥 접촉은 별개다.

## 9. Walkthrough — Classes and Configs

출처: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/walkthrough/api_env_design.html

공식 단원을 기존 quickstart_lab Cartpole 코드로 읽는다. 목적은 설정 객체와 실행 중 로봇 객체, 종료 판정과 실제 재시작을 구분하는 것이다. 새 코드 작성·시뮬레이션 실행은 이번 단계에 포함하지 않는다.

- QuickstartLabEnvCfg는 @configclass로 정의한 설정 묶음이다. sim·scene·robot_cfg도 각각 설정 객체이며, 설정을 만들었다고 로봇이 이미 생성된 것은 아니다.
- Articulation은 관절로 연결된 여러 물체를 다루는 객체다. Cartpole에서는 수레·막대·관절을 함께 다룬다. env.py의 _setup_scene에서 Articulation(self.cfg.robot_cfg)로 생성하고, clone_environments로 복제하며 scene.articulations["robot"]에 등록한다. prim_path는 Stage 안의 경로다.
- 실행 함수: _pre_physics_step은 행동을 받아 저장, _apply_action은 힘 명령 적용, _get_observations는 정책 입력 구성, _get_rewards는 보상 계산, _get_dones는 종료·시간 초과 판정, _reset_idx는 지정한 환경 상태 초기화. DirectRLEnv가 정해진 절차에서 이 함수들을 호출한다.
- 실제 코드의 action_scale=100N은 _apply_action에서 행동에 곱해 수레 관절 힘 명령이 된다. max_cart_pos=3m는 _get_dones의 종료 조건에 사용된다. 설정은 사용하는 코드와 함께 읽는다.

읽기 순서: tasks/direct/quickstart_lab 아래 quickstart_lab_env_cfg.py에서 robot_cfg를 찾고, quickstart_lab_env.py의 _setup_scene에서 self.cfg.robot_cfg 사용·복제·등록을 확인한다. 이어 _get_dones와 _reset_idx의 역할 차이를 확인한다. 이 단계의 복습 문제: ① robot_cfg는 설정/실행 중 로봇 중 무엇이며 이를 받는 생성 클래스는 무엇인가? ② 4개 중 env=2만 종료 시 초기화할 환경은 무엇이며 판정 함수와 초기화 함수는 무엇인가? 사용자 답변 대기. 이후 공식 Environment Design 단원으로 진행할 예정.

### 중간 점검: 전체 위치와 코드 읽기의 종료 기준

2026-10-05 사용자는 현재 단원을 학습하기 전에 전체 목차·직접 로봇 제작과의 관련성·끝나는 기준을 확인해 달라고 요청했다. Quickstart 첫 순회와 Project Structure를 거쳐 공식 Walkthrough 5개 단원 중 2번째 Classes and Configs를 안내한 상태다. 단원 수는 전체 Isaac Sim 숙련도나 제작 진행률을 뜻하지 않는다. Isaac Sim은 로봇 모델·물리·센서 등을 시뮬레이션하는 기반이고 Isaac Lab은 그 위에서 학습 환경과 훈련을 구성하는 도구다. 전체 문서는 순서대로 모두 수강해야 하는 한 과정이 아니다.

실제 성과는 설치, Ant 두 정책 학습·저장·재실행, 정책별 4개 에피소드 평가와 결과 해석이다. 안내에 따라 수행한 경험이며 독립적으로 새 과제를 설계하는 능력까지 검증한 것은 아니다. 목표 속도 추종·안정적 보행 검증은 남아 있고, 자작 로봇의 구조·질량·관절 모델 작성 및 실물 기구·모터·회로 설계·제작은 미착수다. 현재 학습은 미래 로봇의 동작을 훈련·시험하는 부분에 직접 관련되며 하드웨어 설계를 대체하지 않는다.

코드 읽기의 종료 기준: 설정을 소비해 로봇을 생성하는 곳, 행동·관측·보상·종료·초기화의 수정 위치를 자료를 보며 찾고 역할을 설명한다. 함수 이름 암기나 라이브러리 내부 구현 완독은 요구하지 않는다. 현재 단원의 복습을 확인한 다음 공식 Environment Design에서 로봇 교체와 동작의 가시적인 실습으로 연결한다. 이후 필요한 설명은 실습에서 막힌 지점에 한정한다. 첫 프로젝트 완료 기준은 기존 로봇의 평지 보행 학습·정책 저장/재실행·목표 속도 추종과 넘어짐 평가로 유지한다. 이 점검 자체에는 새 복습 문제나 실행 과제를 추가하지 않는다.

Isaac Sim 제작 관련 별도 문서 경로: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/introduction/quickstart_index.html 의 Robot Setup Tutorials(기본 형상 조립·관절·센서·로봇 설정). 향후 필요한 부분을 선택해서 사용하며 현재 전체 과정에 일괄 추가하지 않는다.

Classes and Configs 답변 확인: 사용자가 “설정, Articulation / env=2, _get_dones, _reset_idx”라고 답해 모두 정답이다. 해당 읽기 단원을 마치고 다음 실습으로 이동한다.

## 10. Walkthrough — Environment Design: Jetbot 생성·바퀴 구동

공식 원문: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/walkthrough/technical_env_design.html
웹 조회 실패 시 로컬 v2.3.2의 docs/source/setup/walkthrough/technical_env_design.rst로 원문을 확인했다. 원문은 Cartpole을 Jetbot으로 바꾸고 2개 바퀴 관절 속도를 행동, 몸체 기준 질량중심 선속도 3성분을 관측으로 사용한다. 첫 보상은 속력 크기인 임시 보상이며 원하는 방향·목표 속도 추종을 완성한 것이 아니다.

이번 안내는 원문 구조를 유지하면서 Jetbot 설정을 env_cfg에 함께 두어 파일 수를 줄인다. 사용자는 기존 env_cfg.py·env.py를 .cartpole.txt로 복사 보존하고 두 파일 전체를 입력한다. 기존 Gym 등록 ID와 클래스 이름을 유지하므로 재설치하지 않는다. 새 scripts/drive_jetbot.py는 학습 전 확인용 보충 코드이며 1환경·좌우 바퀴 목표 5rad/s·600환경 스텝을 실행한다. 물리 dt=1/120s, decimation=2이므로 총 가상 시간10초이고 에피소드 제한5초마다 초기화한다. 벽시계 기준으로 지나치게 빨리 끝나지 않도록 각 환경 스텝을 약1/60초로 맞춘다. 화면에 Jetbot이 나타나고 바퀴가 움직이며 출발 위치로 돌아오는지가 확인 대상이다.

Cartpole의 힘 명령(N)과 달리 Jetbot 행동은 좌우 바퀴의 목표 각속도(rad/s)다. 모델의 구동 설정이 목표 속도를 따라가도록 힘/토크를 계산한다. 목표와 실제 속도는 다를 수 있다. 이번에는 일정한 명령을 주므로 정책 학습·가중치 갱신은 없다. 원문 예시 대비 보상은 현재 상태에서 직접 읽고 환경별 1차원 텐서로 반환하며 종료도 환경별 bool 텐서, 초기화는 몸체와 관절을 함께 복원한다. 로컬 DirectRLEnv·Articulation API를 읽어 대조했지만 시뮬레이션 실행은 하지 않았다.

사용자 입력·실행 결과 대기. 복습: ① 명령값5의 의미는 몸체5m/s인가 바퀴5rad/s인가? ② 일정한 속도로 움직였다는 이유로 정책이 학습됐다고 할 수 있는가? 다음 단계는 실제 움직임 확인 후 좌우 바퀴 속도 차이의 효과를 짧게 비교하는 것이다.
복습 답변: 바퀴 목표 각속도5rad/s 및 학습 여부X는 정답이다. “총0.8바퀴”는 “초당 약0.8바퀴를 목표로 함”으로 보완했다. 라디안은 중심각이 차지하는 원호 길이 s를 반지름 r로 나눈 값(s/r)이다. 한 바퀴의 원호는 원둘레2πr이므로 한 바퀴=2πrad≈6.283rad=360°이며 바퀴 크기와 무관하다. 실제로5rad/s를 일정하게 유지한다면 1초에5/(2π)≈0.796바퀴, 2초에약1.59바퀴다. 명령 목표와 실제 회전은 구분한다. 이번 스크립트는 고정 명령을 주며 정책 추론·학습을 수행하지 않는다. Jetbot의 실제 이동·5초 초기화는 사용자의 구체적 관찰 보고를 아직 기다린다.

Jetbot 기준 실행 결과 확인: 사용자가 이동과 약5초 가상 시간마다 초기 위치로 돌아오는 현상을 확인했다. 고정 명령 [5,5] 구동 실습 완료이며 정책 학습은 하지 않았다.

다음은 행동의 물리적 의미를 확인하는 짧은 보충 실습이다. scripts/drive_jetbot.py 전체 코드를 --left/--right 인자로 목표 각속도를 선택하도록 안내한다(기본값은 각각5rad/s). 사용자가 기존 실행 파일을 drive_jetbot_straight.txt로 복사 보존하고 입력한다. --left 5 --right 2로 오른쪽 바퀴 목표만 낮춘다. 같은 크기의 바퀴가 전진하며 큰 미끄러짐 없이 구른다면 왼쪽 바퀴가 더 긴 경로를 가므로 로봇 자신의 오른쪽으로 곡선을 그리는 것이 예상이다. 화면 좌우와 로봇 기준 좌우는 구분한다. 이를 좌우 속도 차이로 조향하는 차동 구동이라고 부른다. 실제 곡선 이동 결과는 아직 미확인이다. 5초 초기화·10초 총 실행은 유지한다. 복습: [5,2]에서 더 느리게 돌도록 명령한 바퀴는 어느 쪽인가? 좌우 명령을 [2,5]로 바꾸면 회전 방향은 어떻게 되는가? 비교 후 추가 주행 실험을 늘리지 않고 공식 학습 단계로 이어간다.

참고: https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_simulation/mobile_robot_controllers.html
차동 구동 복습: 사용자는 [5,2]에서 오른쪽이 더 느리고 [2,5]에서는 왼쪽으로 휘어진다고 정확히 예측했다. “2라디안을 움직인다”는 총각도 표현을 목표 각속도2rad/s로 정정했다. 실제로 일정한2rad/s를 유지하면 1초에2rad, 3초에6rad를 회전한다. 이번 두 명령은 둘 다 전진 방향이며 회전 경로 차이는 좌우 속도 차이에서 생긴다. 숫자는 힘의 크기나 방향을 직접 지정하는 값이 아니다. 실제 [5,2] 실행에서 곡선 이동을 관찰했는지는 아직 확인하지 않았다.

### Jetbot 첫 정책 학습

사용자가 [5,2] 명령의 실제 곡선 이동을 확인했다. 고정 바퀴 명령 보충 실습을 마치고 공식 Environment Design 마지막의 학습 연결을 안내한다. 다음 Training the Jetbot: Ground Truth는 방향 명령·표시 화살표·관측/보상 변경을 포함하는 별도 단계이며 아직 시작하지 않는다.

현재 로컬 env_cfg는 행동2개·몸체 기준 선속도 관측3개, env.py 보상은 현재 몸체 선속도의 크기, 에피소드5초다. skrl_ppo_cfg.yaml은 PPO·rollouts32·기본4800스텝이다. 정책이 관측으로 좌우 바퀴 목표 각속도를 출력하고 PPO가 경험과 보상으로 파라미터를 갱신한다. 보상은 전진/후진을 구분하지 않고 목표 방향·목표 속도도 없으므로 후진이 학습되어도 현 보상과 모순되지 않는다.

사용자 실행 명령(Anaconda Prompt, env_isaaclab 활성화, 작업 폴더 C:\makerobot\IsaacLab):

```bat
isaaclab.bat -p C:\makerobot\quickstart_lab\scripts\skrl\train.py --task Template-Quickstart-Lab-Direct-v0 --num_envs 32 --max_iterations 150 --device cuda:0 --seed 42 agent.agent.experiment.directory=jetbot_speed
```

150×rollouts32=4800환경 스텝이며 병렬 환경32개의 경험으로 한 정책을 학습한다. Ant 때의rollouts16과 다르다. 기존 파일 편집 없이 Hydra 인자로 로그 폴더만 jetbot_speed로 바꾼다. 로그 예상 위치는 C:\makerobot\IsaacLab\logs\skrl\jetbot_speed\날짜시각_ppo_torch, 정책은 그 안 checkpoints의 .pt 파일이다. 완료 기준은4800/4800·Training time·정상 종료와 실제 체크포인트 파일 확인이며 좋은 주행 달성과 구분한다. dir /s /b C:\makerobot\IsaacLab\logs\skrl\jetbot_speed\*.pt 로 저장을 확인하도록 안내한다. 결과/저장 경로를 받은 뒤 해당 정책 재생으로 이어간다. 소스·설정만 읽어 확인했고 학습은 대신 실행하지 않았다. 사용자 학습 결과 대기.

복습: 같은 크기의 전진/후진 속도는 현재 보상에서 차별되는가? 학습 진행률100%가 좋은 주행 달성을 보장하는가? 둘 다 보장/차별하지 않는다는 근거를 확인한다.
학습 복습 답변 확인: 사용자는 방향과 무관하게 속력이 같으면 보상이 같고, 스텝 완료는 정해진 학습량 실행을 뜻한다고 답했다. 두 답과 근거 모두 정확하다. Jetbot 학습 종료 로그와 실제 체크포인트 저장은 아직 확인하지 않았다.


### Jetbot 학습 완료 및 저장 정책 재생 안내

사용자 로그로4800/4800·Training time183.83초·Simulation App Shutting Down을 확인했다. 성능 경고 뒤에도 학습은 끝까지 진행됐으며 이 출력에는 학습 중단 오류가 없다. 사용자 파일 목록에480스텝 간격 체크포인트와best_agent.pt가 있다. 마지막 정책은 C:\makerobot\IsaacLab\logs\skrl\jetbot_speed\2026-10-05_22-51-23_ppo_torch\checkpoints\agent_4800.pt이며 로컬 읽기 전용 조회에서도30069바이트 파일 존재를 확인했다. 저장 설정의4800스텝도 확인했다. 주행 성능 검증은 아직 별개다.

다음 사용자 실행은 quickstart_lab/scripts/skrl/play.py에 위 체크포인트를 명시하고 --task Template-Quickstart-Lab-Direct-v0 --num_envs 1 --device cuda:0 --seed 42 --real-time를 전달한다. agent.agent.experiment.directory=jetbot_speed 및 env.viewer.eye=[2.5,2.5,1.8], env.viewer.lookat=[0,0,0.2]로 로그 표시와 카메라를 맞춘다. 로컬 play.py는 체크포인트를 로드하고 eval 모드·inference_mode에서 정책의 mean_actions를 사용하며 학습 업데이트나 새 체크포인트 저장은 수행하지 않는다. 이는 과거 동작 녹화 재생이 아니라 현재 관측마다 행동을 계산하는 실행이다.

사용자는2~3개 에피소드 동안 전진/후진/회전/정지와5초 초기화를 관찰하고 창을 닫는다. 이전 보충 스크립트와 달리10초 자동 종료는 아니다. 관찰 결과는 아직 미확인이다. 복습은 원하는 방향으로 움직이게 하려면 정책의 관측에 어떤 목표 정보를 추가해야 하는지 묻는다. 결과 확인 후 공식 Ground Truth의 방향 명령 단계로 이어간다.

Jetbot 저장 정책 재생 결과: 사용자가 agent_4800.pt 재생에서 직선 전진을 관찰했다. 재실행 확인 완료이며 방향 명령 추종 성능을 검증한 것은 아니다. 사용자는 지정 방향으로 이동하도록 보상을 바꾸자고 제안했다. 보상 설계 방향은 맞지만, 목표가 바뀌는 제어를 위해서는 현재 목표 방향을 정책 관측에도 제공해야 한다. 동일한 정지 상태에서 목표만 좌/우로 다를 때 현재 속도3성분만 입력하면 정책은 두 요청을 구별할 수 없다. 보상은 학습 시 행동 결과를 평가하고, 관측은 행동 선택에 필요한 정보를 전달한다. 현재 feedforward 정책은 보상을 행동 입력으로 받지 않는다. 방향은 좌표계를 맞춰 해석해야 하며 현재 방향과 목표 방향을 함께 제공하거나 상대 방향으로 표현할 수 있다.

다음 공식 Ground Truth 단계는 목표 방향 명령 생성과 현재/목표 방향 화살표 표시다. 관측에 명령을 넣고 보상을 조정하는 구체적 실습은 이어지는 Exploring the RL problem에서 다룬다. 이번에는 개념 보충과 재생 결과 기록만 했으며 방향 명령 코드 변경은 아직 하지 않았다. 복습: 어느 방향으로 가야 하는지 알려주는 것은 관측, 해당 방향으로 잘 갔는지 평가하는 것은 보상.

방향 기준 보충: 관측/보상 빈칸 답은 모두 정답이다. 사용자가 왼쪽의 기준과 세밀한 방향 지정 여부를 질문했다. 다음 공식 예제의 목표는 세계 좌표계의 방향 벡터이며, 로봇 기준 왼쪽과 구분한다. 설명용으로 세계+X를동쪽,+Y를북쪽으로 정하면 목표[0,1,0]은북쪽이다. 로봇이동쪽을보면왼쪽90°,북쪽을보면회전불필요,서쪽을보면오른쪽90°로 같은 목표의 상대 방향이 달라진다. 동서남북은 설명용 명칭이지 지리적 나침반과 자동 연결된 것이 아니다. 방향 벡터로45°·90°·임의각도 모두 표현할 수 있고, 이는 목적지 좌표나 이동거리와도 다르다. 관측에는 센서 상태뿐 아니라 목표 명령을 포함할 수 있으나 바퀴별 정답 속도를 알려주는 것은 아니다. 목표와 현재 상태를 입력받아 바퀴 행동을 선택하는 관계를 정책이 학습한다. 예측 문제: 북쪽 목표에서 로봇이 이미북쪽을바라보면 계속왼쪽회전/북쪽으로직진 중 무엇이 목표에 맞는가? 아직 답변 대기. 목표 명령 실습 코드는 미변경이다.

### Ground Truth — 목표 방향과 화살표 표시

사용자는 북쪽 목표에 이미 정렬된 로봇은 북쪽으로 직진한다고 정확히 답했다. 세계 기준 목표와 로봇 기준 좌우의 차이를 예시에서 구분했다.

공식 training_jetbot_gt.rst를 읽어 목표 명령 생성·현재/목표 방향 표시 단계로 진행한다. 사용자가 기존 quickstart_lab_env.py를 quickstart_lab_env.speed.txt로 보존한 뒤 채팅의 전체 교체 코드를 입력한다. cfg·정책 관측3개·속력 보상은 유지한다. 환경마다 초기화 때 세계 XY 평면의 무작위 단위 방향을 생성하며, 한 에피소드 동안 목표 방향은 고정된다. 청록색 화살표는 몸체의 앞 방향, 빨간색 화살표는 목표 방향이다. 두 화살표의 위치는 로봇을 따라 이동하지만 빨간색의 세계 기준 방향은 초기화 전까지 유지된다. 화살표는 사람이 보는 표시이며 정책 관측에 자동으로 들어가지 않는다.

공식 예제의 각도 사분면 처리를 atan2로 간소화하고 장치는 self.device를 사용한다. atan2로 구한 yaw는 세계 Z축 주위의 회전각(rad)이며 quat_from_euler_xyz는 표시용 회전 표현으로 변환한다. 화살표가 겹쳐 가려지는 것을 줄이기 위해 현재 방향은 몸체 위0.35m, 목표 방향은0.55m에 표시한다. _get_observations에서 현재 상태로 표시를 갱신한다. 몸체·관절 초기화는 기존 동작을 유지한다. 라이브러리 소스와 인자·텐서 크기를 대조했으며 시뮬레이션은 실행하지 않았다.

기존 scripts/skrl/play.py로 jetbot_speed/2026-10-05_22-51-23_ppo_torch/checkpoints/agent_4800.pt를 재생한다. --num_envs 1 --device cuda:0 --seed 42 --real-time 및 카메라 eye=[2.5,2.5,1.8], lookat=[0,0,0.2]를 사용한다. 확인 기준은 두 색 화살표 표시, 에피소드5초 초기화마다 새 목표 방향 표시다. 기존 정책에는 목표가 입력되지 않아 빨간 화살표를 따라가지 않아도 정상이다. 학습은 진행하지 않는다. 실제 코드 입력·실행 결과는 대기 중이다. 복습: 로봇이 회전하면 현재 방향/고정 목표 중 어느 화살표 방향이 함께 바뀌는가? 목표 표시만으로 정책이 목표를 알 수 있는가? 다음 단계는 결과 확인 후 공식 Exploring the RL problem의 관측·보상 연결이다.
Ground Truth 답변 확인: 사용자는 실행 중 로봇이 회전하지 않는다고 보고했다. 회전하면 청록색 방향만 몸체와 함께 변하고, 빨간색은 목표 방향이므로 유지되며, 표시만으로 정책이 목표를 알 수 없다고 정확히 답했다. 회전은 실제 실행의 필수 관찰이 아니라 가정 문제였음을 명확히 했다. 기존 속력 정책의 관측·행동 계산을 유지했으므로 목표 표시만 추가해도 목표를 향한 회전이 새로 생기지는 않는다. 빨간색은 에피소드 안에서 세계 기준 방향이 고정되며 위치는 로봇을 따라 이동하고 초기화 때 방향이 다시 추출된다. 두 화살표 표시와 초기화 때 변화에 대한 별도 명시적 관찰 보고는 아직 없다. 새 실습이나 코드 변경 없이 결과 해석과 정답 확인을 진행했다.

## 11. Walkthrough — Exploring the RL problem: 첫 방향 학습

공식 원문: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/walkthrough/training_jetbot_reward_exploration.html
로컬 v2.3.2 RST와 현재 코드·ArticulationData·DirectRLEnv 호출 순서를 읽어 확인했다. 사용자 요청에 따라 원문의 첫 시도(관측9개, 덧셈 보상)를 진행한다. 이어지는 상대 방향 관측3개·곱셈/지수 보상 개선은 아직 하지 않는다.

관측은 세계 기준 질량중심 선속도XYZ(m/s)·각속도XYZ(rad/s) 6개와 목표 단위 방향XYZ 3개를 합친9개다. 각속도는 여기서 바퀴가 아닌 몸체가 회전하는 빠르기다. 현재 몸체 방향 자체는 이 첫 관측에 직접 포함되지 않아 완성된 설계가 아니며, 다음 원문 개선에서 상대 방향으로 표현한다. 목표 방향은 에피소드마다 무작위로 설정한다.

보상은 몸체 앞 방향의 부호 있는 속도 + 방향 일치도다. 방향 일치도는 세계 기준 몸체 앞 단위벡터와 목표 단위벡터의 내적이며, 같은 방향1·직각0·정반대-1이다. 앞 방향 벡터는 quat_apply(root_link_quat_w, FORWARD_VEC_B)로 구한다. 속도0.2m/s 전진일 때 환경 보상은 같은 방향1.2·직각0.2·정반대-0.8이다. 보상은 설계한 수치 점수이고 물리적 속도 단위 자체가 아니다. 기존 YAML의 rewards_shaper_scale=0.1은 유지한다. 보상 계산에서 현재 상태를 직접 읽어 이전 관측 시점의 방향이 남지 않게 한다. 환경별 보상은 (num_envs,)로 반환한다.

2026-10-05 최신 사용자 위임에 따라 파일 복사·백업·코드 반영은 어시스턴트가 수행하고, 전체 코드·설명·명령·복습은 채팅에 계속 제공하는 방식으로 변경했다. 기존 env_cfg.py와 env.py를 각각 quickstart_lab_env_cfg.markers.txt·quickstart_lab_env.markers.txt로 복사하고 수정 전 원본과 SHA256 해시 일치를 확인했다. 관측9개·새 관측 구성·덧셈 보상을 실제 파일에 반영하고 두 파일 ast.parse 및 compile 문법 검사를 통과했다. 이전 채팅 주석의 世界는 세계로 바로잡았다. 마커·목표 생성·초기화·행동은 유지한다. 기존 관측3개 정책과 입력 크기가 달라 --checkpoint 없이 새 학습을 시작한다. 시뮬레이션과 학습은 실행하지 않았으며 사용자가 실행할 차례다.

사용자 명령(Anaconda Prompt, env_isaaclab, C:\makerobot\IsaacLab):

```bat
isaaclab.bat -p C:\makerobot\quickstart_lab\scripts\skrl\train.py --task Template-Quickstart-Lab-Direct-v0 --num_envs 32 --max_iterations 150 --device cuda:0 --seed 42 agent.agent.experiment.directory=jetbot_direction_v1
```

150×rollouts32=4800환경 스텝의 짧은 첫 학습이며 이전 속력 학습과 같은 규모다. --headless를 넣지 않아 창이 열리는 실행이다. 학습 완료·저장 확인은 dir /s /b C:\makerobot\IsaacLab\logs\skrl\jetbot_direction_v1\*.pt로 한다. 4800/4800·Training time·agent_4800.pt 경로를 받은 다음 새 정책을 명시해 재생한다. 학습 중 탐색 행동이나 첫 설계의 한계 때문에 방향 추종이 불완전할 수 있으며 성공을 미리 보장하지 않는다. 코드 반영·문법 검사는 완료했고 실제 학습·정책 저장 결과는 대기 중이다.

복습: ① 몸체 속도가 같아도 목표 방향이 바뀌면 이번 정책 관측은 달라지는가? ② 목표 방향을 정확히 바라보며 정지한 경우 전진 속도+방향 일치도 보상은 얼마인가? 두 번째는 덧셈 보상의 한계를 검토하기 위한 예측 질문이다.

### 방향 정책 v1 학습 완료·관측 값 보충·재생 안내

2026-10-06 사용자 로그에서4800/4800·Training time188.36초·정상 종료와 체크포인트 목록을 확인했다. 마지막 정책은 C:\makerobot\IsaacLab\logs\skrl\jetbot_direction_v1\2026-10-05_23-55-02_ppo_torch\checkpoints\agent_4800.pt이다. 읽기 전용 조회로32501바이트 파일 존재와 현재 관측9개 코드를 확인했다. 실제 방향 추종 성능은 아직 재생 전이다.

복습② 정지 상태에서 목표 방향과 일치하면 환경 보상0+1=1이라는 답은 정답이다. 즉 현재 덧셈 보상은 이동하지 않아도 점수를 준다. 이것만으로 실제 정책이 정지를 학습했다고 단정하지 않고 재생에서 관찰한다. 복습① 사용자는 관측이 고정되어 있으므로 목표가 달라도 바뀌지 않는다고 답했다. 고정되는 것은 입력 항목·순서·개수(9개)이며, 매 스텝 채우는 값은 현재 속도·목표에 따라 달라진다고 보완했다. 정지 상태의 속도6개가 모두0이어도 동쪽 목표[1,0,0]와 북쪽 목표[0,1,0]는 마지막3개의 값이 다르다. 목표는 현재 코드에서 에피소드 안에 유지되고 초기화 때 새로 추출되며 속도는 움직임에 따라 바뀐다. 재생 중 정책 가중치가 유지되는 것과 입력 관측 값이 바뀌는 것은 별개다.

다음은 기존 scripts/skrl/play.py로 위 agent_4800.pt를 명시하고 --task Template-Quickstart-Lab-Direct-v0 --num_envs 1 --device cuda:0 --seed 42 --real-time agent.agent.experiment.directory=jetbot_direction_v1 env.viewer.eye=[2.5,2.5,1.8] env.viewer.lookat=[0,0,0.2]로 실행한다. 정책 업데이트 없이 현재 관측으로 행동을 계산한다. 3~4개 에피소드 동안 목표가 바뀔 때 청록색이 빨간색 방향으로 회전하는지, 정렬 후 이동/정지하는지 관찰한 뒤 창을 닫는다. 어시스턴트는 재생하지 않았고 사용자 결과 대기. 확인 문제: 정지 상태에서 목표만 동쪽에서 북쪽으로 바뀌면 입력 개수는 __개로 유지되고 마지막 __개의 값이 바뀐다.

### 방향 정책 v1 재생 결과와 v2 관측 개선

2026-10-06 사용자는 관측 항목9개는 유지되고 목표 방향3개의 값이 바뀐다고 정확히 답했다. v1 재생에서는 목표 방향을 잘 맞추지 못하거나, 맞춘 뒤에도 회전을 계속해 목표 방향을 지나치는 현상을 보고했다. 방향을 지나친다는 관찰은 목표 방향을 넘어서 회전한다는 의미로 해석했다. 현재 정책은 매 순간 좌우 바퀴 속도를 선택하며 방향 정렬→회전 정지→직진의 절차가 별도로 구현된 것은 아니다. 관찰만으로 지나침의 원인을 단정하지 않는다.

공식 Exploring the RL problem의 Reward and Observation Tuning 첫 변경을 적용했다. v1의 세계 속도6개+목표3개에는 몸체의 현재 방향이 직접 포함되지 않아, 같은 목표·정지 상태에서 몸체 방향이 달라도 입력이 같아질 수 있다. v2는 현재 앞 방향과 목표 방향의 내적(alignment), 외적의Z성분(side), 몸체 기준 전진 속도로 관측3개를 구성한다. 두 벡터는 세계 좌표로 계산하지만 결과는 몸체와 목표의 상대적인 관계다. 평지에서 목표가 정면이면(1,0), 왼쪽90°면(0,1), 오른쪽90°면(0,-1), 정반대면(-1,0)이다. 앞 두 값은 각도 자체(rad)가 아니며, 몸체가 수평이면 각각 상대각의cos·sin에 해당한다. 전진 속도 단위는m/s다. 왼쪽으로 회전해 목표를 지나면 side는 양수→0→음수로 바뀌어 목표가 이제 오른쪽에 있음을 입력으로 전달한다. side=0만으로 정면이라고 판단할 수 없고 alignment와 함께 봐야 한다.

어시스턴트가 v1 파일을 quickstart_lab_env_cfg.direction_v1.txt·quickstart_lab_env.direction_v1.txt로 백업하고 SHA256 해시 일치를 확인한 뒤 관측3개 코드를 반영했다. Python 구문 검사 통과, AST 비교로 _get_rewards·_apply_action·_reset_idx를 변경하지 않았음을 확인했다. 보상은 여전히 전진 속도+방향 일치도다. 시뮬레이션·학습은 실행하지 않았다. 개선 효과나 지나침 해소는 미확인이다.

다음 사용자 학습은 기존 train.py에서 --task Template-Quickstart-Lab-Direct-v0 --num_envs 32 --max_iterations 150 --device cuda:0 --seed 42 agent.agent.experiment.directory=jetbot_direction_v2로 실행한다. 4800스텝으로 규모를 유지하고 기존 체크포인트는 불러오지 않는다. v1은 입력9개라 맞지 않고, 예전 jetbot_speed는 입력3개라도 의미가 달라 재사용하지 않는다. dir /s /b C:\makerobot\IsaacLab\logs\skrl\jetbot_direction_v2\*.pt로 경로를 확인한다. 학습 종료·agent_4800.pt 경로를 받은 뒤 같은 관찰 조건으로 재생한다. 1회 비교는 학습 성능의 일반적 우열을 입증하지 않는다.

복습: ① 정지 상태에서 목표가 몸체 왼쪽90°에 있으면 새 관측[일치도,좌우성분,전진속도]는 무엇인가? ② 목표 방향을 지나도록 왼쪽으로 조금 더 돌았다면 목표는 몸체 오른쪽에 있으므로 side 부호는 무엇인가? 답변·학습 결과 대기.
2026-10-06 사용자 상태 확인: 위 v2 설명은 아직 학습·복습하지 않았고 v2 훈련도 시작 전이다. Git 저장소 정리 후 이 지점에서 재개한다. 코드 준비 완료와 사용자 이해·학습 실행 완료를 구분한다.

## 기록 원칙

실습과 학습에 필요한 핵심 개념·실행 방법·관찰 결과를 정리한다. 자격증 유무 같은 단순 정보 질문은 사용자가 기록을 요청하지 않는 한 넣지 않는다. Python 기초 설명과 코드의 줄별 해설은 반복하지 않는다. 더 깊은 설명은 필요해질 때 추가하고, 예상과 실제 결과는 구분한다.

