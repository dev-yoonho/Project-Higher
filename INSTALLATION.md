# Isaac Lab 설치 복구와 실행 확인

확인일: 2026-10-04. 환경: Windows 11, RTX 5070 12GB, `env_isaaclab`.

사용자가 초기 설치를 진행한 뒤 `isaaclab` 패키지가 누락된 상태를 공유했다. 이후 사용자가 이번 설치 완료를 대신 수행해 달라고 명시적으로 요청해, 어시스턴트가 패키지를 복구하고 최소 실행을 확인했다. 이후 학습은 다시 사용자가 직접 실행하는 방식으로 진행한다.

## 최종 결과

Isaac Lab 핵심 패키지와 RSL-RL 설치, CUDA 물리 시뮬레이션, Cartpole 환경의 GUI·headless 실행을 확인했다. **보행 정책 학습은 아직 시작하지 않았다.** Cartpole은 설치 검사에만 사용했으며 첫 보행 로봇으로 선정한 것이 아니다.

| 검사 | 결과 |
|---|---|
| 소스 | v2.3.2, 커밋 `37ddf626871758333d6ed89cf64ad702aef127d0` |
| 핵심 Python 패키지 | `isaaclab==0.54.2`, 로컬 소스 editable 설치 확인 |
| 학습 라이브러리 | `rsl-rl-lib==3.1.2`, `OnPolicyRunner` import 성공 |
| 빈 장면 | headless, `cuda:0`, 120 physics step 성공 및 종료 코드 0 |
| Cartpole headless | 최종 환경에서 4개 환경, 32 step, 유한한 관측·보상 확인, 정상 종료 |
| Cartpole GUI | 최종 환경에서 4개 환경, 120 step, 유한한 관측·보상 확인, 정상 종료 |
| HDF5 | 최종 GUI·headless 모두 메모리 내 데이터 쓰기·읽기 성공, h5py 3.13.0 / HDF5 1.14.6 |
| 공식 실행 래퍼 | 최종 headless 검사는 `isaaclab.bat -p`로 실행, 프로젝트 Python 경로 확인 |
| 의존성 검사 | `pip check` 경고 1건 남음. 아래의 FastAPI·Starlette 요구사항 충돌 |

GUI 검사는 실행 로그와 종료 결과를 기준으로 한다. 화면을 직접 보고 외관을 평가한 것은 아니다. 종료 코드뿐 아니라 로그의 `INSTALL_CHECK_PASS`도 확인했다. 초기 GUI 실패에서도 종료 코드가 0으로 나왔으므로 코드 0만으로 성공을 판단하지 않는다.

최종 GUI 검사는 약 21초에 종료됐다. 앞선 첫 Cartpole GUI 성공 실행에는 초기 렌더링 준비를 포함해 약 84초가 걸렸다. 이는 사용자 보고의 Isaac Sim 단독 창 시작 시간 약 1분과 서로 다른 측정이다. 보행 학습 속도나 최대 병렬 환경 수의 근거로 사용하지 않는다.

## 해결한 문제

1. **`isaaclab` 설치 누락:** `flatdict==4.0.1`의 빌드가 `ModuleNotFoundError: No module named 'pkg_resources'`로 실패했다. 격리된 빌드 환경이 setuptools 84.0.0을 선택한 상태였다. 빌드 환경에만 setuptools 80.9.0과 wheel 0.45.1을 지정해 flatdict를 설치한 뒤 핵심 패키지를 설치했다. 실행 환경의 setuptools는 83.0.0을 유지했다.
2. **TensorDict 충돌:** 0.14.2는 일반 Python에서 import됐지만, Isaac Sim 시작 후 RSL-RL을 통해 import할 때 Windows access violation이 재현됐다. 0.9.0으로 고정한 뒤 같은 검사와 Cartpole 실행이 통과했다. 0.9.1은 `pyvers`가 요구하는 packaging 버전이 Isaac Sim과 충돌해 설치하지 않았다.
3. **GUI의 h5py DLL 오류:** h5py 3.16.0은 GUI 확장 시작 후 `_errors` DLL 로딩에 실패했다. 3.11.0에서는 실행됐지만 HDF5 빌드·런타임 버전 경고가 남았다. 최종적으로 HDF5 1.14.6을 사용하는 3.13.0으로 맞췄으며, GUI·headless 실행과 데이터 쓰기·읽기 검사에서 해당 경고가 사라졌다.
4. **추가 의존성 정리:** 누락된 torchaudio 2.7.0+cu128을 설치했다. Isaac Sim 요구사항에 맞춰 psutil 5.9.8을 사용하고, 이 버전과 충돌하던 IPython을 8.37.0으로 맞췄다. packaging 23.0과 충돌하던 wheel 0.47.0은 0.45.1로 조정했다.

처음 만든 유한 스텝 검사에서는 빈 장면의 종료 콜백을 정리하지 않아 종료 대기가 발생했다. 검사 스크립트에 공식 `SimulationContext`의 콜백·인스턴스 정리 방식을 적용했고, 재검사에서 정상 종료했다. 해당 검사 프로세스만 종료했으며 사용자의 다른 프로그램은 종료하지 않았다.

Isaac Lab 원본 소스, NVIDIA 드라이버, 시스템 CUDA Toolkit은 수정하지 않았다. 원본 저장소에는 복구 전부터 `2.7.0+cu128`이라는 미추적 파일이 있었다. 내용은 설치 배치의 출력 한 줄이며 그대로 보존했다.

## 남아 있는 의존성 경고

```text
fastapi 0.115.7 has requirement starlette<0.46.0,>=0.40.0, but you have starlette 0.49.1.
```

Isaac Sim 5.1.0의 `isaacsim-kernel`은 FastAPI 0.115.7을 요구하고, Isaac Lab v2.3.2는 Starlette 0.49.1을 요구한다. FastAPI의 Starlette 상한과 겹치지 않으므로 이 공식 요구사항을 모두 유지하면서 `pip check`를 통과시키는 조합은 없다. [공식 저장소의 동일 문제 보고](https://github.com/isaac-sim/IsaacLab/issues/4145)도 확인했다.

설치 메타데이터를 고쳐 경고를 숨기거나, 경고 제거만을 위해 공식 버전 조합을 바꾸지 않았다. **로컬 GUI·headless 시뮬레이션은 위 검사에서 통과했지만, 웹 API·스트리밍 기능의 호환성은 검증하지 않았다.** 그러므로 의존성이 완전히 무충돌인 환경이라고 기록하지 않는다. 해당 기능이 필요해질 때 이 항목을 다시 검토한다.

## 다시 실행하는 방법

Anaconda Prompt에서:

```bat
conda activate env_isaaclab
cd /d C:\makerobot\IsaacLab
isaaclab.bat -p C:\makerobot\scripts\check_install.py --headless --task Isaac-Cartpole-v0 --steps 32
isaaclab.bat -p C:\makerobot\scripts\check_install.py --task Isaac-Cartpole-v0 --steps 120
```

각 명령은 지정한 스텝만 실행한 뒤 종료한다. `INSTALL_CHECK_PASS`를 확인한다. 학습이나 체크포인트 생성은 수행하지 않는다.

사용자가 다음에 직접 살펴볼 공식 첫 예제:

```bat
isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

이 예제는 자동 종료하지 않으며 창을 닫아 종료한다. 장면 생성, 시간 간격, `reset()`과 `step()`의 역할을 이해하는 데 사용한다.

## 2026-10-05 Quickstart용 skrl 추가

사용자가 `pip show`로 isaaclab 0.54.2, isaaclab_tasks 0.11.12, isaaclab_rl 0.4.7의 editable 설치와 skrl 누락을 확인했다. 원문의 학습 예제를 따르기 위해 사용자가 아래 명령으로 추가 설치했다.

```bat
python -m pip install "skrl==1.4.3"
python -c "import skrl; from skrl.utils.runner.torch import Runner; print('skrl:', skrl.__version__); print('PyTorch Runner import: OK')"
git describe --tags --exact-match
```

사용자 보고: `skrl: 1.4.3`, `PyTorch Runner import: OK`, `v2.3.2` 모두 예상대로 출력. 이 단계에서 실제 학습은 아직 미확인이다. 기존 패키지 목록 스냅샷은 이 추가 설치 전 기록이다.

## 버전과 복구 기록

- [최종 패키지 목록](setup/packages-verified.txt): 설치된 버전의 스냅샷. 전체 설치 절차를 대체하는 파일은 아니다.
- [복구 전 패키지 목록](setup/packages-before-repair.txt)
- [실행 패키지 제약](setup/runtime-constraints.txt): PyTorch·NumPy 등 기준 버전과 이번 호환성 조정 보존.
- [빌드 전용 제약](setup/build-constraints.txt): flatdict 빌드 문제 재발 방지.
- [설치 로그](isaaclab-core-install.log), [최종 의존성 검사](setup/pip-check.txt)
- [최종 headless 검사 로그](setup/check-cartpole-headless-final.log), [최종 GUI 검사 로그](setup/check-cartpole-gui-final.log)
- [검사 스크립트](scripts/check_install.py)

기존 환경에서 수행한 핵심 복구 명령은 아래와 같다. 이미 복구한 현재 환경에서 다시 실행할 필요는 없다. Lab 보조 패키지들은 사용자가 실행한 초기 설치에서 이미 설치된 상태였다.

```bat
python -m pip install flatdict==4.0.1 --build-constraint C:\makerobot\setup\build-constraints.txt
python -m pip install -e C:\makerobot\IsaacLab\source\isaaclab --constraint C:\makerobot\setup\runtime-constraints.txt --build-constraint C:\makerobot\setup\build-constraints.txt
python -m pip install torchaudio==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128 --constraint C:\makerobot\setup\runtime-constraints.txt
python -m pip install wheel==0.45.1 psutil==5.9.8 ipython==8.37.0 tensordict==0.9.0 h5py==3.13.0 --constraint C:\makerobot\setup\runtime-constraints.txt
```

근거: [flatdict 빌드 코드](https://github.com/gmr/flatdict/blob/4.0.1/setup.py), [pip 빌드 제약 문서](https://pip.pypa.io/en/stable/user_guide/#build-constraints), [Isaac Lab Windows 사용자들의 TensorDict 실행 문제 보고](https://github.com/isaac-sim/IsaacLab/discussions/5373), [h5py 3.13의 HDF5 1.14.6 적용 기록](https://docs.h5py.org/en/3.14.0/whatsnew/3.13.html). 외부 사례는 진단 참고로만 사용했고, 성공 판단은 위 로컬 실행 결과를 기준으로 했다.
