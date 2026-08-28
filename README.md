# 🌊 Surfline Castellón v2.0 AI · Plataforma Local de Previsión

Plataforma inteligente de previsión de oleaje adaptada específicamente para las 11 playas de la provincia de Castellón, con motor físico costero (sombra del Cabo de Oropesa), visión por computador en webcams, preavisos con 2 días de antelación y alertas personalizadas por Telegram y WhatsApp.

---

## 📍 Las 11 Playas Monitorizadas
1. **Planetario** (Grao de Castellón)
2. **Gurugú** (Castellón)
3. **Pirámides** (Benicàssim)
4. **El Palaciet** (Benicàssim)
5. **Voramar** (Benicàssim · Cámaras Axis 1 y 2)
6. **La Renegà** (Oropesa del Mar)
7. **Burriana** (Playa del Arenal)
8. **Nules** (Espigones)
9. **Almenara** (Casablanca)
10. **Peñíscola Norte** (Castillo)
11. **Vinaròs** (Playa del Fortí)

---

## 🚀 Cómo Publicar la Web en GitHub Pages (1 Clic)

1. Entra en tu repositorio: [https://github.com/mralcachofino-cyber/surfline-castellon](https://github.com/mralcachofino-cyber/surfline-castellon)
2. Ve a **Settings** > **Pages** (en el menú de la izquierda).
3. En **Branch**, selecciona `main` y la carpeta `/ (root)`.
4. Pulsa en **Save**.
5. ¡Listo! En 1 minuto tendrás tu web activa en:  
   👉 `https://mralcachofino-cyber.github.io/surfline-castellon/`

---

## 🔐 Configuración de Secretos en GitHub (Para Alertas Automáticas)

Para que el robot pueda enviar los avisos por Telegram y WhatsApp:
1. En tu repositorio, ve a **Settings** > **Secrets and variables** > **Actions**.
2. Pulsa en **New repository secret** y añade:
   * `TELEGRAM_BOT_TOKEN`: `8650554341:AAF2DNZZcI5MkK2GDgrqC6hrAh6zhL1lFO4`
   * `TELEGRAM_CHANNEL_ID`: `-1003885396809`
   * `ADMIN_PHONE`: `+34687688854`
   * `ADMIN_CALLMEBOT_KEY`: `7360308`

---

## 💻 Subir estos archivos a tu GitHub

Desde la terminal o consola en esta carpeta:
```bash
git init
git add .
git commit -m "🚀 Despliegue inicial Surfline Castellon v2.0 AI"
git branch -M main
git remote add origin https://github.com/mralcachofino-cyber/surfline-castellon.git
git push -u origin main
```
