import setuptools

# with open('README.md', 'r') as f:
#   long_description = f.read()

setuptools.setup(
  name='video_invisible_watermark',
  version='0.1.0',
  author='Fernando Otero',
  author_email='oteromartinez.f@gmail.com',
  description='A program form embedding ivisible watermak os video frames',
  # long_description=long_description,
  # long_description_content_type='text/markdown',
  # url='https://github.com/FerOtero/WatermarkingForense.git',
  packages=setuptools.find_packages(),
  install_requires=[
      # 'opencv-python>=4.1.0.25',
      # 'torch',
      # 'onnx',
      # 'onnxruntime',
      # 'Pillow>=6.0.0',
      # 'PyWavelets>=1.1.1',
      # 'numpy>=1.17.0',
      'invisible-watermark>=0.1.5'
  ],
  # scripts=['video-invisible-watermark'],
  classifiers=[
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      'Operating System :: POSIX :: Linux',
  ],
  # # Python 3.6 tested in Ubuntu 18.04 LTS.
  python_requires='>=3.6',
  # include_package_data=True,
)