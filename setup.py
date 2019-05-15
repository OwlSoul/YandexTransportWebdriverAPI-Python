from distutils.core import setup
setup(
  # How you named your package folder
  name = 'yandex_transport_webdriver_api',
  # Chose the same as "name"
  packages = ['yandex_transport_webdriver_api'],
  # Start with a small number and increase it with every change you make
    version = '1.0.2',
  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  license='MIT',
  # Give a short description about your library
  description = 'Kind of an API to Yandex Transport/Masstransit service, to be used in '
                'conjunction with YandexTransportProxy server '
                '(see here: https://github.com/OwlSoul/YandexTransportProxy).',
  # Type in your name
  author = 'Yury D.',
  # Type in your E-Mail
  author_email = 'SoulGate@yandex.ru',
  # Provide either the link to your github or to your website
  url = 'https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python',
  # I explain this later on
    download_url = 'https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/archive/1.0.2.tar.gz',
  # Keywords that define your package best
  keywords = ['Yandex', 'Transport', 'Masstransit', 'WebDriver'],
  # I get to this in a second
  install_requires=[],
   # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
  classifiers=[
    'Development Status :: 3 - Alpha',
     # Define that your audience are developers
    'Intended Audience :: Developers',
     # Again, pick a license
    'License :: OSI Approved :: MIT License',
     # Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
