# NEBULA — rifa/ruleta en vivo

Dos páginas estáticas (`nebula-admin.html` y `nebula-publico.html`) que comparten
estado en tiempo real a través de Supabase, más un servidor local mínimo en
Python (`server.py`) para abrirlas sin problemas de CORS/file://.

## 1. Arrancar el servidor local

Necesitas Python (ya lo tienes: 3.12). Desde esta carpeta:

```
python server.py
```

Esto abre `http://localhost:8787/nebula-admin.html` en tu navegador y **solo
escucha en 127.0.0.1**: ningún otro dispositivo de tu red puede acceder,
solo esta PC. También puedes hacer doble clic en `iniciar-nebula.bat`.

Para un evento donde quieras que la gente vea la ruleta desde su celular en
la misma WiFi:

```
python server.py --lan
```

Esto expone el servidor en tu red local. La página de admin también quedaría
visible en la red, pero eso no es un problema real (ver sección de
seguridad abajo) — de todas formas comparte con tus invitados solo el link
de **nebula-publico.html** (botón "🔗 Link público" en el admin).

## 2. Crear el backend en Supabase (gratis)

1. Crea un proyecto en https://supabase.com.
2. Ve a **SQL Editor** y corre esto para crear la tabla de estado:

```sql
create table nebula_state (
  id text primary key,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

insert into nebula_state (id, data) values (
  'main',
  '{"participants":[],"history":[],"settings":{"removeWinner":true,"epic":true,"rainbow":false},"draw":null,"version":1}'
);

alter table nebula_state enable row level security;

-- cualquiera puede LEER el estado (así funciona la página pública sin login)
create policy "lectura publica" on nebula_state
  for select using (true);

-- solo tu correo de admin puede ESCRIBIR (cambia el email por el tuyo)
create policy "solo admin escribe" on nebula_state
  for update using (auth.jwt() ->> 'email' = 'TU_CORREO_ADMIN@ejemplo.com')
  with check (auth.jwt() ->> 'email' = 'TU_CORREO_ADMIN@ejemplo.com');
```

3. Activa **Realtime** para la tabla: en el dashboard ve a
   **Database → Replication** y activa `nebula_state`, o corre:

```sql
alter publication supabase_realtime add table nebula_state;
```

4. Crea tu usuario admin en **Authentication → Users → Add user** (email +
   contraseña). **No actives el registro público (sign-up)** — así solo
   existe la cuenta que tú creaste a mano y nadie más puede registrarse.
   Si además quieres exigir que el correo esté confirmado antes de poder
   iniciar sesión, actívalo en **Authentication → Providers → Email**.

5. En **Project Settings → API** copia el **Project URL** y el **anon
   public key**, y pégalos en `nebula-config.js`:

```js
window.NEBULA_CONFIG = {
  SUPABASE_URL: "https://xxxxxxxx.supabase.co",
  SUPABASE_ANON_KEY: "ey...",
  RAFFLE_ID: "main"
};
```

Recarga `nebula-admin.html`, inicia sesión con el correo/contraseña que
creaste y ya puedes agregar participantes y sortear.

## 3. ¿Cuál es la mejor protección para el admin?

Pediste que solo tu PC pudiera ser "admin". **No hice eso** porque no es una
protección real y te la explico:

- El anon key de Supabase vive en el navegador (es público por diseño) y las
  llamadas van directo del navegador a Supabase, no pasan por tu servidor
  local. Bloquear por IP en `server.py` no protegería nada: cualquiera con
  el anon key podría llamar a Supabase directamente desde otra máquina,
  sin pasar jamás por tu `server.py`.
- Detectar "tu PC" por IP pública tampoco es confiable: tu IP cambia (redes
  dinámicas, WiFi de otro lugar, VPN), y cualquiera en tu misma red/oficina
  compartiría esa IP.
- Un fingerprint de navegador (user-agent, canvas, etc.) se resetea con
  borrar cookies o modo incógnito — no es seguridad, es cosmético.

Lo que sí protege de verdad, y que la página ya trae integrado, es:

1. **Autenticación real con contraseña** (Supabase Auth) en vez de "eres tú
   si vienes de tal IP". Ya está implementado en `nebula-admin.html`.
2. **Un solo usuario admin**, creado a mano en el dashboard de Supabase, sin
   registro público abierto — así nadie más puede *crear* una cuenta que
   pase el login.
3. **Row Level Security** en la tabla: cualquiera puede leer (para que la
   página pública funcione sin login), pero solo tu correo puede escribir
   — esto se aplica en el servidor de Supabase, no en el navegador, así que
   no se puede saltar editando el JS.
4. Guarda la contraseña de esa cuenta en un gestor de contraseñas y no la
   compartas; comparte solo el link de `nebula-publico.html`, nunca el de
   `nebula-admin.html`.

Con eso, "quién es admin" queda definido por *quién sabe la contraseña*, que
es un control real, en vez de intentar adivinar "qué PC es la tuya" — algo
que ni el propio navegador puede garantizarle a un servidor.

Si además quieres una capa extra sencilla: deja `server.py` corriendo sin
`--lan` cuando no estés en un evento, así ni siquiera se puede cargar
`nebula-admin.html` desde fuera de tu PC mientras trabajas en ella
localmente.
