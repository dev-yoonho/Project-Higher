import torch
import torchvision

print("Pytorch:", torch.__version__)
print("torchvision:", torchvision.__version__)
print("CUDA 빌드:", torch.version.cuda)
print("GPU 사용 가능:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("현재 Python 환경에서 CUDA GPU를 사용할 수 없습니다.")

print("GPU:", torch.cuda.get_device_name(0))

x = torch.ones((256, 256), device="cuda:0")
result = x @ x

print("결과 장치:", result.device)
print("결과 평균:", result.mean().item())