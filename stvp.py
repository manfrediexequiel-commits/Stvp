import React, { useState, useEffect, useMemo } from 'react';
import { 
  Shield, 
  Search, 
  Download, 
  LogOut, 
  Users, 
  IdCard, 
  Calendar, 
  ChevronRight,
  Lock,
  RefreshCw,
  AlertCircle,
  Loader2
} from 'lucide-react';

// Enlaces de Google Sheets (Exportación CSV)
const URL_SOCIOS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv";
const URL_FAMILIA_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv";

const App = () => {
  const [dbSocios, setDbSocios] = useState([]);
  const [dbFamilia, setDbFamilia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dniInput, setDniInput] = useState('');
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const [showAdmin, setShowAdmin] = useState(false);
  const [adminPass, setAdminPass] = useState('');

  // Función genérica para parsear CSV desde Google Sheets
  const parseCSV = (csvText) => {
    const rows = csvText.split('\n').map(row => {
      // Manejo básico de comas dentro de comillas si fuera necesario
      return row.split(',').map(cell => cell.replace(/^"|"$/g, '').trim());
    });
    const headers = rows[0].map(h => h.toLowerCase().replace(/ /g, '_'));
    
    return rows.slice(1).map(row => {
      let obj = {};
      headers.forEach((header, i) => {
        obj[header] = row[i];
      });
      return obj;
    });
  };

  // Función para cargar ambas bases de datos
  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [resSocios, resFamilia] = await Promise.all([
        fetch(URL_SOCIOS_CSV),
        fetch(URL_FAMILIA_CSV)
      ]);

      const textSocios = await resSocios.text();
      const textFamilia = await resFamilia.text();

      const dataSocios = parseCSV(textSocios).filter(s => s.dni);
      const dataFamilia = parseCSV(textFamilia).filter(f => f.dni_titular || f.dni_familiar);

      setDbSocios(dataSocios);
      setDbFamilia(dataFamilia);
      setLoading(false);
      setError('');
    } catch (err) {
      console.error("Error sincronizando:", err);
      setError("Error de conexión con el servidor de datos.");
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  // Lógica de Identificación
  const handleLogin = (e) => {
    e.preventDefault();
    if (!dniInput) return;

    // Buscamos coincidencia exacta de DNI
    const socio = dbSocios.find(s => String(s.dni) === String(dniInput));
    if (socio) {
      setUser(socio);
      setError('');
    } else {
      setError('DNI no encontrado en el padrón de afiliados.');
    }
  };

  const handleLogout = () => {
    setUser(null);
    setDniInput('');
    setError('');
  };

  // Filtrar familiares vinculados al titular logueado
  const familiaresVinculados = useMemo(() => {
    if (!user) return [];
    return dbFamilia.filter(f => String(f.dni_titular) === String(user.dni));
  }, [user, dbFamilia]);

  // Colores según jerarquía/rango
  const getTheme = (miembro) => {
    const m = String(miembro || "").toUpperCase();
    if (m.includes('COMISIÓN') || m.includes('DIRECTIVA')) {
      return {
        bg: 'from-amber-700 via-amber-900 to-black',
        border: 'border-amber-400',
        accent: 'text-amber-300',
        label: 'bg-amber-500/20'
      };
    } else if (m.includes('DELEGADO')) {
      return {
        bg: 'from-emerald-700 via-emerald-900 to-black',
        border: 'border-emerald-400',
        accent: 'text-emerald-300',
        label: 'bg-emerald-500/20'
      };
    } else {
      return {
        bg: 'from-blue-700 via-blue-900 to-black',
        border: 'border-blue-400',
        accent: 'text-blue-300',
        label: 'bg-blue-500/20'
      };
    }
  };

  const theme = user ? getTheme(user.miembro || user.cargo) : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
        <div className="relative mb-6">
           <Shield className="w-16 h-16 text-blue-600 animate-pulse" />
           <Loader2 className="w-16 h-16 text-blue-400 animate-spin absolute top-0 left-0 opacity-50" />
        </div>
        <p className="text-slate-400 font-bold tracking-widest text-xs uppercase animate-pulse">Sincronizando Base de Datos STVP</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-8">
      {/* Header Superior */}
      <header className="max-w-md mx-auto flex items-center justify-between mb-8">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-500/20">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-black text-lg tracking-tighter leading-none">STVP</h1>
            <p className="text-[8px] font-bold text-blue-500 tracking-[0.3em] uppercase">Digital Wallet</p>
          </div>
        </div>
        <button 
          onClick={() => setShowAdmin(!showAdmin)}
          className="p-2 hover:bg-slate-800 rounded-full transition-all text-slate-600 hover:text-blue-400"
        >
          <Lock className="w-5 h-5" />
        </button>
      </header>

      <main className="max-w-md mx-auto">
        {!user ? (
          /* VISTA INICIAL / LOGIN */
          <div className="bg-slate-900/50 border border-slate-800/50 p-8 rounded-[2.5rem] backdrop-blur-2xl shadow-2xl animate-in fade-in zoom-in-95 duration-700">
            <div className="text-center mb-10">
              <div className="w-20 h-20 bg-blue-600/10 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-500/20">
                <IdCard className="w-10 h-10 text-blue-500" />
              </div>
              <h2 className="text-2xl font-black mb-2 text-white tracking-tight">Portal del Afiliado</h2>
              <p className="text-slate-500 text-sm font-medium px-4">Consulte su credencial digital y la de su grupo familiar.</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div className="relative group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  type="text" 
                  inputMode="numeric"
                  placeholder="Ingrese su DNI"
                  className="w-full bg-slate-800/50 border-2 border-slate-700/50 rounded-2xl py-5 pl-12 pr-4 focus:border-blue-500 focus:bg-slate-800 transition-all outline-none font-bold text-lg"
                  value={dniInput}
                  onChange={(e) => setDniInput(e.target.value.replace(/\D/g, ''))}
                />
              </div>
              
              {error && (
                <div className="flex items-center gap-3 text-red-400 text-xs bg-red-400/5 p-4 rounded-2xl border border-red-400/20 animate-shake">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="font-bold uppercase tracking-wide">{error}</span>
                </div>
              )}

              <button 
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-black py-5 rounded-2xl shadow-2xl shadow-blue-600/30 transition-all active:scale-[0.97] flex items-center justify-center gap-2 text-sm uppercase tracking-widest"
              >
                Acceder a mi Credencial
              </button>
            </form>
          </div>
        ) : (
          /* VISTA DE LA CREDENCIAL ACTIVA */
          <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-700">
            
            {/* Tarjeta Visual */}
            <div className={`relative overflow-hidden aspect-[1.58/1] rounded-[2rem] border-2 ${theme.border} bg-gradient-to-br ${theme.bg} shadow-2xl p-8 flex flex-col justify-between group`}>
              {/* Elementos Estéticos de Fondo */}
              <div className="absolute -right-20 -top-20 w-64 h-64 bg-white/10 rounded-full blur-[80px] group-hover:bg-white/20 transition-all duration-1000" />
              <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-black/40 rounded-full blur-[80px]" />
              
              <div className="flex justify-between items-start relative z-10">
                <div className="flex items-center gap-3">
                  <div className="bg-white/10 p-2 rounded-lg backdrop-blur-md border border-white/10">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-[9px] tracking-[0.4em] font-black text-white/70 uppercase">Sindicato STVP</span>
                </div>
                <div className="text-[10px] font-black text-white/40 uppercase tracking-widest border border-white/10 px-2 py-1 rounded-md">
                   {user.miembro?.split(' ')[0] || 'ACTIVO'}
                </div>
              </div>

              <div className="relative z-10">
                <h3 className="text-2xl md:text-3xl font-black tracking-tighter mb-2 text-white uppercase drop-shadow-2xl">
                  {user.nombre || user.apellido_y_nombre}
                </h3>
                <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.1em] ${theme.label} ${theme.accent} border border-white/5 shadow-inner`}>
                  <div className={`w-2 h-2 rounded-full animate-pulse bg-current opacity-70`} />
                  {user.cargo || user.miembro}
                </div>
              </div>

              <div className="flex justify-between items-end relative z-10">
                <div className="bg-black/30 p-3 rounded-2xl backdrop-blur-md border border-white/5">
                  <p className="uppercase text-white/30 text-[7px] mb-1 font-black tracking-widest">Documento Identidad</p>
                  <p className="text-sm font-black tracking-[0.2em] text-white">{user.dni}</p>
                </div>
                <div className="text-right bg-black/30 p-3 rounded-2xl backdrop-blur-md border border-white/5">
                  <p className="uppercase text-white/30 text-[7px] mb-1 font-black tracking-widest">Vencimiento</p>
                  <p className="text-sm font-black text-white">{user.vence || 'AL DÍA'}</p>
                </div>
              </div>
            </div>

            {/* Acciones de Usuario */}
            <div className="grid grid-cols-2 gap-4">
              <button className="flex flex-col items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 py-5 rounded-3xl transition-all border border-slate-800 shadow-xl active:scale-95 group">
                <div className="p-2 bg-blue-500/10 rounded-xl group-hover:bg-blue-500/20 transition-colors">
                  <Download className="w-5 h-5 text-blue-500" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Descargar PDF</span>
              </button>
              <button 
                onClick={handleLogout}
                className="flex flex-col items-center justify-center gap-2 bg-slate-900 hover:bg-red-950/20 py-5 rounded-3xl transition-all border border-slate-800 shadow-xl text-slate-500 hover:text-red-400 active:scale-95 group"
              >
                <div className="p-2 bg-slate-800 rounded-xl group-hover:bg-red-500/10 transition-colors">
                  <LogOut className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest">Cerrar Sesión</span>
              </button>
            </div>

            {/* Listado de Grupo Familiar */}
            <div className="bg-slate-900/60 rounded-[2.5rem] border border-slate-800/50 p-8 backdrop-blur-xl shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                   <div className="p-2 bg-blue-600/10 rounded-xl">
                      <Users className="w-5 h-5 text-blue-500" />
                   </div>
                   <h4 className="font-black text-lg tracking-tight">Grupo Familiar</h4>
                </div>
                <span className="bg-blue-500/10 text-blue-400 text-[10px] px-3 py-1 rounded-full border border-blue-500/20 font-black uppercase tracking-tighter">
                  {familiaresVinculados.length} Registros
                </span>
              </div>
              
              <div className="space-y-3">
                {familiaresVinculados.length > 0 ? familiaresVinculados.map((f, i) => (
                  <div key={i} className="flex items-center justify-between p-5 bg-slate-800/30 rounded-3xl border border-slate-700/30 hover:bg-slate-800/60 transition-all cursor-pointer group hover:border-blue-500/30">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-2xl bg-slate-700/50 flex items-center justify-center font-black text-slate-400 group-hover:text-blue-400 transition-colors">
                        {f.nombre?.charAt(0) || 'F'}
                      </div>
                      <div>
                        <p className="font-black text-sm text-slate-100 uppercase tracking-tight">{f.nombre}</p>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                          {f.parentesco} <span className="mx-1 opacity-30">•</span> DNI {f.dni_familiar}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-blue-500 transition-all translate-x-0 group-hover:translate-x-1" />
                  </div>
                )) : (
                  <div className="text-center py-10 border-2 border-dashed border-slate-800 rounded-[2rem]">
                    <p className="text-slate-600 text-[10px] font-black uppercase tracking-[0.2em] leading-relaxed">
                      No se encuentran familiares<br/>vinculados a este titular
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Pie de Página */}
            <footer className="text-center py-8">
              <div className="flex items-center justify-center gap-2 text-slate-700 mb-2">
                <Calendar className="w-3 h-3" />
                <p className="text-[9px] font-black uppercase tracking-[0.3em]">Estado: Padrón Activo 2025</p>
              </div>
              <p className="text-[8px] text-slate-800 font-bold uppercase tracking-widest italic">Seguridad Garantizada por Sistema STVP Digital</p>
            </footer>
          </div>
        )}

        {/* Panel Administrativo (Sync) */}
        {showAdmin && (
          <div className="mt-8 p-8 bg-slate-900 border border-blue-500/20 rounded-[2rem] shadow-2xl animate-in slide-in-from-top-4">
            <div className="flex items-center justify-between mb-6">
              <h5 className="font-black text-xs text-white flex items-center gap-2 uppercase tracking-widest">
                <RefreshCw className="w-4 h-4 text-blue-500" /> Control de Sincronización
              </h5>
              <button onClick={() => setShowAdmin(false)} className="text-slate-600 hover:text-white transition-colors">
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <input 
                type="password" 
                placeholder="Clave de acceso"
                className="w-full bg-black/40 border border-slate-800 rounded-2xl p-4 text-sm outline-none focus:border-blue-500 text-white font-bold"
                value={adminPass}
                onChange={(e) => setAdminPass(e.target.value)}
              />
              <button 
                onClick={() => {
                  if(adminPass === 'stvp2025') cargarDatos();
                  else alert('Acceso denegado');
                }}
                className="w-full bg-slate-800 hover:bg-blue-600 text-white py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all shadow-lg active:scale-95"
              >
                Forzar Refresco de Datos
              </button>
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800">
                <div className="text-center">
                  <p className="text-[8px] text-slate-500 font-bold uppercase">Socios</p>
                  <p className="text-xl font-black text-blue-500">{dbSocios.length}</p>
                </div>
                <div className="text-center">
                  <p className="text-[8px] text-slate-500 font-bold uppercase">Familiares</p>
                  <p className="text-xl font-black text-emerald-500">{dbFamilia.length}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
