import numpy as np
import cv2
import matplotlib.pyplot as plt


def ideal_lowpass_filter(image, cutoff_freq):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建理想低通滤波器
    filter_mask = np.zeros((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    filter_mask[
        cy - cutoff_freq : cy + cutoff_freq, cx - cutoff_freq : cx + cutoff_freq
    ] = 1
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def ideal_highpass_filter(image, cutoff_freq):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建理想低通滤波器
    filter_mask = np.ones((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    filter_mask[
        cy - cutoff_freq : cy + cutoff_freq, cx - cutoff_freq : cx + cutoff_freq
    ] = 0
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def butterworth_lowpass_filter(image, cutoff_freq, order):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建巴特沃斯低通滤波器
    filter_mask = np.zeros((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
            filter_mask[i, j] = 1 / (1 + (dist / cutoff_freq) ** (2 * order))
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def butterworth_highpass_filter(image, cutoff_freq, order):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建巴特沃斯低通滤波器
    filter_mask = np.ones((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
            filter_mask[i, j] = 1 - (1 / (1 + (dist / cutoff_freq) ** (2 * order)))
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def gaussian_lowpass_filter(image, cutoff_freq):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建高斯低通滤波器
    filter_mask = np.zeros((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
            filter_mask[i, j] = np.exp(-0.5 * (dist / cutoff_freq) ** 2)
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def gaussian_highpass_filter(image, cutoff_freq):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建高斯低通滤波器
    filter_mask = np.ones((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
            filter_mask[i, j] = 1 - (np.exp(-0.5 * (dist / cutoff_freq) ** 2))
    # 将滤波器应用于频域图像
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def Laplace_highpass_filter(image, cutoff_freq):
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 进行二维傅里叶变换
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    # 构建拉普拉斯滤波器
    filter_mask = np.ones((height, width, 2), np.float32)
    cx, cy = width // 2, height // 2
    u, v = np.mgrid[-1 : 1 : 2.0 / height, -1 : 1 : 2.0 / width]
    D = np.sqrt(u**2 + v**2)
    kernel = -4 * np.pi**2 * D**2
    filter_mask = kernel
    # (5) 在频率域修改傅里叶变换: 傅里叶变换 点乘 滤波器传递函数
    dftFilter = np.zeros(height, width)  # 快速傅里叶变换的尺寸(优化尺寸)
    dft_shift_filtered = dft_shift * filter_mask
    # 进行逆变换，将图像转换回空域
    dft_filtered_shifted = np.fft.ifftshift(dft_shift_filtered)
    img_filtered = cv2.idft(dft_filtered_shifted)
    img_filtered = cv2.magnitude(img_filtered[:, :, 0], img_filtered[:, :, 1])
    return img_filtered


def homomorphic_filter(image, d0=10, rl=0.5, rh=2.0, c=4, h=2.0, l=0.5):
    height, width = image.shape[0], image.shape[1]
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    gray_fftshift = np.fft.fftshift(dft)  # FFT傅里叶变换

    M, N = np.meshgrid(
        np.arange(-width // 2, width // 2), np.arange(-height // 2, height // 2)
    )
    D = np.sqrt(M**2 + N**2)  # 计算距离
    Z = (rh - rl) * (1 - np.exp(-c * (D**2 / d0**2))) + rl  # H(u,v)传输函数
    dst_fftshift = Z * gray_fftshift
    dst_fftshift = (h - l) * dst_fftshift + l
    dst_ifftshift = np.fft.ifftshift(dst_fftshift)
    dst_ifft = np.fft.ifft2(dst_ifftshift)  # IFFT逆傅里叶变换
    img_filtered = np.real(dst_ifft)  # IFFT取实部
    img_filtered = np.exp(img_filtered) - 1  # 还原
    img_filtered = np.uint8(np.clip(img_filtered, 0, 255))
    return img_filtered


# 读取图像
image_1 = cv2.imread(r"C:\Users\A403\Desktop\characterTestPattern688.jpg", 0)  # 以灰度模式读取
image_2 = cv2.imread(r"C:\Users\A403\Desktop\lena.jpg", 0)  # 以灰度模式读取

# 执行理想低通滤波
cutoff_frequency_1 = 5  # 截止频率
cutoff_frequency_2 = 10  # 截止频率
cutoff_frequency_3 = 20  # 截止频率
cutoff_frequency_4 = 30  # 截止频率
order = 2
filtered_image_11 = homomorphic_filter(image_1)
filtered_image_12 = homomorphic_filter(image_1)
filtered_image_13 = homomorphic_filter(image_1)
filtered_image_14 = homomorphic_filter(image_1)

filtered_image_21 = homomorphic_filter(image_2)
filtered_image_22 = homomorphic_filter(image_2)
filtered_image_23 = homomorphic_filter(image_2)
filtered_image_24 = homomorphic_filter(image_2)


# 显示原始图像和滤波后的图像
plt.subplot(251), plt.imshow(image_1, cmap="gray")
plt.title("O I"), plt.xticks([]), plt.yticks([])
plt.subplot(252), plt.imshow(filtered_image_11, cmap="gray")
plt.title("CF=10"), plt.xticks([]), plt.yticks([])
plt.subplot(253), plt.imshow(filtered_image_12, cmap="gray")
plt.title("CF=20"), plt.xticks([]), plt.yticks([])
plt.subplot(254), plt.imshow(filtered_image_13, cmap="gray")
plt.title("CF=30"), plt.xticks([]), plt.yticks([])
plt.subplot(255), plt.imshow(filtered_image_14, cmap="gray")
plt.title("CF=40"), plt.xticks([]), plt.yticks([])

plt.subplot(256), plt.imshow(image_2, cmap="gray")
plt.title("O I"), plt.xticks([]), plt.yticks([])
plt.subplot(257), plt.imshow(filtered_image_21, cmap="gray")
plt.title("CF=10"), plt.xticks([]), plt.yticks([])
plt.subplot(258), plt.imshow(filtered_image_22, cmap="gray")
plt.title("CF=20"), plt.xticks([]), plt.yticks([])
plt.subplot(259), plt.imshow(filtered_image_23, cmap="gray")
plt.title("CF=30"), plt.xticks([]), plt.yticks([])
plt.subplot(2, 5, 10), plt.imshow(filtered_image_24, cmap="gray")
plt.title("CF=40"), plt.xticks([]), plt.yticks([])

plt.show()
