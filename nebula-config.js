// Config de NEBULA. Pega aquí los datos de TU proyecto de Supabase
// (Project Settings → API). El anon key es seguro de exponer en el
// cliente: la protección real está en las políticas RLS de la tabla
// nebula_state (ver README.md).
window.NEBULA_CONFIG = {
  SUPABASE_URL: "https://udgdpbdoiimpcqhipwuk.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_5SrOpsUuFccozYD9JbVO3Q_s8T7PTgA",
  RAFFLE_ID: "main"                                 // id de la fila en nebula_state; puedes tener varias rifas
};
