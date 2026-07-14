"""Shareable Chipotle-themed web chat channel served at the chat webhook root."""
import inspect
from typing import Awaitable, Callable, Text, Union

from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import BaseHTTPResponse, HTTPResponse, ResponseStream
from rasa.core.channels.channel import UserMessage
from rasa.core.channels.rest import RestInput

# The page is intentionally self-contained so the public /webhooks/chat/ URL is the
# branded widget, rather than a generic REST test panel.
CHAT_PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chipotle order helper</title>
<style>
:root {
  --pepper-red:#A81612; --pepper-dark:#74100d; --cream:#FFF3D7; --green:#2E7D32;
  --bean:#2B2118; --silver:#D9D4C8; --orange:#F26A21; --paper:#FFFCF5;
  --muted:#74695d; --line:#ded5c4; --focus:#155c25; --radius:22px;
}
*{box-sizing:border-box} html,body{height:100%} body{margin:0;min-height:100%;display:grid;place-items:center;padding:24px;color:var(--bean);font-family:Arial,"Helvetica Neue",sans-serif;background:radial-gradient(circle at 10% 0%,#fff7e5 0 16%,transparent 36%),radial-gradient(circle at 95% 90%,#f9d9ad 0 8%,transparent 34%),var(--cream)}
.chat{width:min(100%,450px);height:min(720px,calc(100vh - 48px));display:flex;flex-direction:column;background:var(--paper);border:1px solid rgba(43,33,24,.15);border-radius:var(--radius);overflow:hidden;box-shadow:0 24px 70px rgba(74,37,14,.23)}
.header{position:relative;isolation:isolate;display:flex;align-items:center;gap:11px;padding:16px 18px 15px;color:#fff;background:var(--pepper-red);overflow:hidden}.header:after{content:"";position:absolute;z-index:-1;inset:auto -35px -31px -20px;height:53px;background:repeating-linear-gradient(105deg,rgba(255,255,255,.18) 0 2px,transparent 2px 8px);transform:rotate(-3deg)}
.seal{width:39px;height:39px;display:grid;place-items:center;border:2px solid #fff3d7;border-radius:50%;background:var(--pepper-dark);box-shadow:0 0 0 3px rgba(255,243,215,.27)}.seal svg{width:24px;height:24px}.title{font-family:Impact,"Arial Narrow",sans-serif;letter-spacing:.55px;font-size:19px;text-transform:uppercase;line-height:1}.sub{margin-top:5px;font-size:11px;letter-spacing:.04em;color:#fff3d7}.online{margin-left:auto;display:flex;align-items:center;gap:5px;font-size:11px;color:#fff3d7}.online i{width:7px;height:7px;border-radius:50%;background:#8ed36b;box-shadow:0 0 0 3px rgba(142,211,107,.2)}
.messages{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:9px;background:linear-gradient(180deg,#fffdf8,#fff9ed)}.intro{padding:8px 3px 2px}.eyebrow{display:inline-flex;align-items:center;gap:6px;color:var(--green);font-size:11px;font-weight:bold;letter-spacing:.09em;text-transform:uppercase}.eyebrow:before{content:"";width:18px;height:2px;background:var(--orange)}h1{margin:8px 0 7px;font-family:Impact,"Arial Narrow",sans-serif;font-size:27px;font-weight:400;letter-spacing:.35px;line-height:1.06;text-transform:uppercase}p{margin:0;color:var(--muted);font-size:14px;line-height:1.45}.start-label{margin:10px 0 0;font-size:12px;font-weight:bold;color:var(--bean)}
.row{display:flex;gap:8px;max-width:88%;align-items:flex-end}.row.user{align-self:flex-end;flex-direction:row-reverse}.avatar{width:25px;height:25px;flex:0 0 25px;display:grid;place-items:center;border-radius:50%;background:var(--green);color:white;font-size:11px;font-weight:bold}.avatar svg{width:15px}.user .avatar{background:var(--bean)}.bubble{padding:10px 12px;border-radius:15px;border-bottom-left-radius:4px;background:#f1eadc;font-size:13.5px;line-height:1.45;white-space:pre-wrap;word-break:break-word}.user .bubble{border-radius:15px 15px 4px 15px;background:var(--pepper-red);color:#fff}.chips{display:flex;flex-wrap:wrap;gap:7px;padding:2px 0 7px}.chip{min-height:36px;border:1px solid var(--green);border-radius:999px;padding:7px 12px;background:#fff;color:#1e6227;font:700 12.5px/1 Arial,sans-serif;cursor:pointer;transition:background .15s,transform .15s}.chip:hover{background:#e8f3dd;transform:translateY(-1px)}.chip:focus-visible,.send:focus-visible,.input:focus-visible{outline:3px solid var(--focus);outline-offset:2px}.typing{align-self:flex-start;color:var(--muted);font-size:12px;padding:8px 11px;background:#f1eadc;border-radius:14px}.composer{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line);background:#fffdf8}.input{min-width:0;flex:1;resize:none;border:1px solid #bcb09e;border-radius:14px;padding:10px 12px;color:var(--bean);font:14px/1.35 Arial,sans-serif;background:#fff}.input::placeholder{color:#756b60}.send{width:43px;border:0;border-radius:13px;background:var(--pepper-red);color:#fff;cursor:pointer}.send:hover:not(:disabled){background:var(--pepper-dark)}.send:disabled{opacity:.5;cursor:not-allowed}.error{color:#8f241b;font-size:13px;background:#fff0e9;border-left:3px solid var(--orange);padding:9px 10px;border-radius:5px}
@media(max-width:520px){body{padding:0}.chat{height:100vh;border:0;border-radius:0}h1{font-size:25px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style></head>
<body><main class="chat" aria-label="Chipotle order support chat">
<header class="header"><div class="seal" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 20c-4.8 0-7-3-7-6.4 0-2.7 1.6-5.1 4.4-6.1-.1-1.5.8-3 2.4-3.7-.2 1.4.2 2.3 1.2 3.1 2.7.2 5.1 2.2 5.1 5.6C18.1 16.9 15.4 20 12 20Z" fill="#FFF3D7"/><path d="M10.2 4.8c.8-.5 1.7-.8 2.7-.8" stroke="#FFF3D7" stroke-width="1.5" stroke-linecap="round"/></svg></div><div><div class="title">Chipotle</div><div class="sub">ORDER HELPER</div></div><div class="online"><i></i>Here to help</div></header>
<section class="messages" id="messages" aria-live="polite"><div class="intro" id="intro"><div class="eyebrow">Order support</div><h1>Let’s get your meal sorted.</h1><p>Check when your order will be ready, or tell us what went wrong.</p><div class="start-label">Choose a quick start</div></div><div class="chips" id="starter"><button class="chip">Check my order time</button><button class="chip">I got the wrong order</button><button class="chip">My food quality was poor</button><button class="chip">I’m missing an item</button></div></section>
<form class="composer" id="form"><textarea class="input" id="input" rows="1" placeholder="Tell us about your order…" aria-label="Your message"></textarea><button class="send" id="send" aria-label="Send message" title="Send message"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m21 3-8.4 18-2.6-7.4L3 11 21 3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg></button></form></main>
<script>(function(){const messages=document.getElementById('messages'),input=document.getElementById('input'),form=document.getElementById('form'),sendButton=document.getElementById('send');let sender=localStorage.getItem('chipotle_order_sender');if(!sender){sender='chipotle-web-'+crypto.getRandomValues(new Uint32Array(1))[0].toString(36);localStorage.setItem('chipotle_order_sender',sender)}const icon='<svg viewBox="0 0 24 24" fill="none"><path d="M12 20c-4.8 0-7-3-7-6.4 0-2.7 1.6-5.1 4.4-6.1-.1-1.5.8-3 2.4-3.7-.2 1.4.2 2.3 1.2 3.1 2.7.2 5.1 2.2 5.1 5.6C18.1 16.9 15.4 20 12 20Z" fill="white"/></svg>';function scroll(){messages.scrollTop=messages.scrollHeight}function add(role,text){let row=document.createElement('div');row.className='row '+role;row.innerHTML='<div class="avatar">'+(role==='bot'?icon:'YOU')+'</div><div class="bubble"></div>';row.querySelector('.bubble').textContent=text;messages.appendChild(row);scroll()}function addButtons(buttons){let wrap=document.createElement('div');wrap.className='chips';buttons.forEach(b=>{let button=document.createElement('button');button.className='chip';button.textContent=b.title||b.payload;button.onclick=()=>send(b.payload||b.title);wrap.appendChild(button)});messages.appendChild(wrap);scroll()}function typing(on){let el=document.getElementById('typing');if(on){el=document.createElement('div');el.id='typing';el.className='typing';el.textContent='Checking that for you…';messages.appendChild(el);scroll()}else if(el)el.remove()}function resize(){input.style.height='auto';input.style.height=Math.min(input.scrollHeight,110)+'px'}function send(text){text=(text||'').trim();if(!text)return;document.getElementById('intro')?.remove();document.getElementById('starter')?.remove();add('user',text);input.value='';resize();sendButton.disabled=true;typing(true);fetch('./webhook',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender:sender,message:text})}).then(r=>{if(!r.ok)throw Error();return r.json()}).then(replies=>{typing(false);(replies||[]).forEach(r=>{if(r.text)add('bot',r.text);if(r.buttons?.length)addButtons(r.buttons)})}).catch(()=>{typing(false);let error=document.createElement('div');error.className='error';error.textContent='I couldn’t reach the order helper just now. Check your connection and try again.';messages.appendChild(error);scroll()}).finally(()=>{sendButton.disabled=false;input.focus()})}document.querySelectorAll('#starter .chip').forEach(b=>b.onclick=()=>send(b.textContent));form.onsubmit=e=>{e.preventDefault();send(input.value)};input.oninput=resize;input.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(input.value)}};input.focus()})()</script></body></html>'''


class WebChatInput(RestInput):
    """REST webhook plus a branded GET page at the webhook root."""

    @classmethod
    def name(cls) -> Text:
        return "chat"

    def blueprint(self, on_new_message: Callable[[UserMessage], Awaitable[None]]) -> Blueprint:
        module = inspect.getmodule(self)
        webchat = Blueprint("webchat_{}".format(type(self).__name__), module.__name__ if module else None)

        @webchat.route("/", methods=["GET"])
        async def chat_page(request: Request) -> HTTPResponse:
            return response.html(CHAT_PAGE)

        @webchat.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> Union[ResponseStream, BaseHTTPResponse]:
            return await self.receive_messages(request, on_new_message)

        return webchat
