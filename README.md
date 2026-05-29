\# PyChat - Real Time Django Chat App



A real-time chat application built using Django, Django Channels, WebSockets, HTML, CSS, and JavaScript.



\## Features



\* Real-time messaging

\* Online users indicator

\* Typing indicator

\* Seen message ticks

\* Image sharing

\* Private chat rooms

\* WhatsApp-style UI

\* WebSocket communication using Django Channels



\## Tech Stack



\* Python

\* Django

\* Django Channels

\* Daphne

\* SQLite

\* HTML

\* CSS

\* JavaScript



\## Screenshots



\### Login Page



!\[Login](screenshots/chatlogin.png)



\### Main Chat Screen



!\[Main Chat](screenshots/chatmain.png)



\### Chat Conversation



!\[Chat Conversation](screenshots/chatpawan.png)



\### Image Sharing



!\[Image Shared](screenshots/imageshared.png)



\## Installation



Clone project:



```bash

git clone <your-github-repo-link>

cd realtime\_chat\_app

```



Create virtual environment:



```bash

python -m venv venv

venv\\Scripts\\activate

```



Install requirements:



```bash

pip install -r requirements.txt

```



Run migrations:



```bash

python manage.py migrate

```



Run Django server:



```bash

python manage.py runserver

```



Run Daphne:



```bash

daphne -p 9000 core.asgi:application

```



Open browser:



```text

http://127.0.0.1:9000/

```



\## Author



ESLAVATH MAHESH



