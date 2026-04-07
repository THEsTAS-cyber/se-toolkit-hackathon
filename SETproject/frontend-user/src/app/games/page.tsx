"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../AuthProvider";
import { useFavorites } from "../useFavorites";

interface PriceEntry {
  id: number; region: string; currency: string;
  current_price: number | null; original_price: number | null;
  discount_percent: number | null; collected_at: string; store_url: string | null;
}
interface Game {
  id: number; name: string; cover_url: string | null;
  platforms: string[]; content_type: string | null;
  price_entries: PriceEntry[];
}

const RUB_RATES: Record<string, number> = {
  RUB:1,USD:92,EUR:100,UAH:2.2,GBP:118,PLN:23,TRY:2.5,JPY:0.6,BRL:16,AUD:60,
  ARS:0.08,THB:2.7,INR:1.1,ZAR:5,IDR:0.006,MXN:4.5,KRW:0.07,HKD:12,TWD:2.9,
  SGD:69,MYR:20,SAR:24.5,AED:25,ILS:25,QAR:25.3,KWD:300,BHD:244,OMR:239,
  MAD:9.2,CLP:0.095,COP:0.023,PEN:24.5,UYU:2.3,PYG:0.012,BOB:13.3,CRC:0.18,
  GTQ:12,SVC:10.5,HNL:3.7,NIO:2.5,DOP:1.55,PAB:92,CAD:68,NZD:55,CZK:4.1,
  HUF:0.26,RON:20.2,BGN:51,HRK:13.3,SKK:3.3,ISK:0.67,DKK:13.4,SEK:8.8,
  NOK:8.6,CHF:104,CNY:12.8,
};
const REGION_NAMES: Record<string, string> = {
  ae:"🇦🇪 UAE",ar:"🇦🇷 Argentina",at:"🇦🇹 Austria",au:"🇦🇺 Australia",
  be:"🇧🇪 Belgium",bg:"🇧🇬 Bulgaria",bh:"🇧🇭 Bahrain",bo:"🇧🇴 Bolivia",
  br:"🇧🇷 Brazil",ca:"🇨🇦 Canada",ch:"🇨🇭 Switzerland",cl:"🇨🇱 Chile",
  cn:"🇨🇳 China",co:"🇨🇴 Colombia",cr:"🇨🇷 Costa Rica",cy:"🇨🇾 Cyprus",
  cz:"🇨🇿 Czechia",de:"🇩🇪 Germany",dk:"🇩🇰 Denmark",ec:"🇪🇨 Ecuador",
  es:"🇪🇸 Spain",fi:"🇫🇮 Finland",fr:"🇫🇷 France",gb:"🇬🇧 UK",
  gr:"🇬🇷 Greece",gt:"🇬🇹 Guatemala",hk:"🇭🇰 Hong Kong",hn:"🇭🇳 Honduras",
  hr:"🇭🇷 Croatia",hu:"🇭🇺 Hungary",id:"🇮🇩 Indonesia",ie:"🇮🇪 Ireland",
  il:"🇮🇱 Israel",in:"🇮🇳 India",is:"🇮🇸 Iceland",it:"🇮🇹 Italy",
  jp:"🇯🇵 Japan",kr:"🇰🇷 Korea",kw:"🇰🇼 Kuwait",lb:"🇱🇧 Lebanon",
  lu:"🇱🇺 Luxembourg",mt:"🇲🇹 Malta",mx:"🇲🇽 Mexico",my:"🇲🇾 Malaysia",
  ni:"🇳🇮 Nicaragua",nl:"🇳🇱 Netherlands",no:"🇳🇴 Norway",nz:"🇳🇿 New Zealand",
  om:"🇴🇲 Oman",pa:"🇵🇦 Panama",pe:"🇵🇪 Peru",pl:"🇵🇱 Poland",
  pt:"🇵🇹 Portugal",py:"🇵🇾 Paraguay",qa:"🇶🇦 Qatar",ro:"🇷🇴 Romania",
  ru:"🇷🇺 Russia",sa:"🇸🇦 Saudi Arabia",se:"🇸🇪 Sweden",sg:"🇸🇬 Singapore",
  si:"🇸🇮 Slovenia",sk:"🇸🇰 Slovakia",sv:"🇸🇻 El Salvador",th:"🇹🇭 Thailand",
  tr:"🇹🇷 Turkey",tw:"🇹🇼 Taiwan",ua:"🇺🇦 Ukraine",us:"🇺🇸 USA",
  uy:"🇺🇾 Uruguay",za:"🇿🇦 South Africa",
};

function convertToRub(p: number, c: string) { return p * (RUB_RATES[c] || 1); }
function formatCur(p: number, c: string) {
  const s: Record<string,string> = {USD:"$",EUR:"€",UAH:"₴",GBP:"£",PLN:"zł",TRY:"₺",JPY:"¥",BRL:"R$",AUD:"A$",RUB:"₽"};
  return `${p.toFixed(2)} ${s[c]||c}`;
}

type Platform = "all" | "PS5" | "PS4";
type ContentType = "all" | "game" | "bundle" | "add_on";

export default function GamesPage() {
  const { token } = useAuth();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name"|"cheapest"|"discount">("cheapest");
  const [expandedId, setExpandedId] = useState<number|null>(null);
  const [platform, setPlatform] = useState<Platform>("all");
  const [type, setType] = useState<ContentType>("all");
  const { favIds, toggle: toggleFav } = useFavorites(token);

  useEffect(() => {
    fetch("/api/games?limit=2000").then(r=>r.json()).then(d=>{setGames(d);setLoading(false);}).catch(()=>setLoading(false));
  }, []);

  const getBest = (g: Game) => {
    const v = g.price_entries.filter(e=>e.current_price!=null);
    if(!v.length) return null;
    let best:PriceEntry|null=null, bestRub=Infinity;
    for(const e of v){const r=convertToRub(e.current_price!,e.currency);if(r<bestRub){bestRub=r;best=e;}}
    return best?{entry:best,rub:bestRub}:null;
  };

  const filtered = games
    .filter(g=>g.name.toLowerCase().includes(search.toLowerCase()))
    .filter(g=>platform==="all"||g.platforms.includes(platform))
    .filter(g=>type==="all"||g.content_type===type)
    .sort((a,b)=>{
      if(sortBy==="name") return a.name.localeCompare(b.name);
      if(sortBy==="discount"){
        const aD=Math.max(...a.price_entries.map(e=>e.discount_percent||0));
        const bD=Math.max(...b.price_entries.map(e=>e.discount_percent||0));
        return bD-aD;
      }
      const aB=getBest(a),bB=getBest(b);
      return(aB?.rub??Infinity)-(bB?.rub??Infinity);
    });

  if(loading) return <div className="loading">Loading games...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="title">🎮 PS Store Catalog</h1>
          <p className="subtitle">{games.length} games • {Object.keys(RUB_RATES).length} currencies</p>
        </div>
      </div>

      <div className="filters">
        <input type="text" placeholder="🔍 Search by title..." value={search} onChange={e=>setSearch(e.target.value)} className="search-input"/>
        <div className="filter-group">
          <span className="filter-label">Platform:</span>
          <div className="chip-group">
            {(["all","PS5","PS4"] as Platform[]).map(p=>(
              <button key={p} className={`chip ${platform===p?"chip-active":""}`} onClick={()=>setPlatform(p)}>
                {p==="all"?"All":p}
              </button>
            ))}
          </div>
        </div>
        <div className="filter-group">
          <span className="filter-label">Type:</span>
          <div className="chip-group">
            {([["all","All"],["game","Games"],["bundle","Bundles"],["add_on","DLC"]] as [ContentType,string][]).map(([v,l])=>(
              <button key={v} className={`chip ${type===v?"chip-active":""}`} onClick={()=>setType(v)}>{l}</button>
            ))}
          </div>
        </div>
        <div className="filter-group">
          <span className="filter-label">Sort:</span>
          <div className="chip-group">
            {([["cheapest","💰 Price"],["name","🔤 Name"],["discount","🔥 Discount"]] as [typeof sortBy,string][]).map(([v,l])=>(
              <button key={v} className={`chip ${sortBy===v?"chip-active":""}`} onClick={()=>setSortBy(v)}>{l}</button>
            ))}
          </div>
        </div>
      </div>

      <p className="results-count">Showing: {filtered.length} of {games.length}</p>

      {filtered.length===0?(
        <div className="empty">{games.length===0?"📭 Catalog is empty. Wait for price sync.":"🔍 Nothing found."}</div>
      ):(
        <div className="grid">
          {filtered.map(g=>{
            const best=getBest(g);
            const isExp=expandedId===g.id;
            const isFav=favIds.has(g.id);
            const prices=g.price_entries.filter(e=>e.current_price!=null)
              .map(e=>({...e,rub:convertToRub(e.current_price!,e.currency)}))
              .sort((a,b)=>a.rub-b.rub);
            const maxDisc=Math.max(...g.price_entries.map(e=>e.discount_percent||0));
            return(
              <div key={g.id} className="card">
                <div className="cover-wrapper">
                  {g.cover_url?<img src={g.cover_url} alt={g.name} className="cover"/>:<div className="cover-placeholder">🎮</div>}
                  {g.platforms.length>0&&<div className="platforms">{g.platforms.map(p=><span key={p} className={`plat-badge ${p==="PS5"?"ps5":"ps4"}`}>{p}</span>)}</div>}
                  {maxDisc>0&&<div className="disc-badge">-{maxDisc}%</div>}
                  {token&&<button className={`fav-btn ${isFav?"fav-active":""}`} onClick={()=>toggleFav(g.id)} title="Add to wishlist">{isFav?"❤️":"🤍"}</button>}
                </div>
                <h2 className="game-name">{g.name}</h2>
                {best&&(
                  <div className="best-price">
                    <span className="best-label">Best:</span>
                    <span className="best-value">{formatCur(best.entry.current_price!,best.entry.currency)}</span>
                    <span className="best-region">{REGION_NAMES[best.entry.region]||best.entry.region}</span>
                    <span className="best-rub">≈ {best.rub<1?best.rub.toFixed(2):best.rub.toFixed(0)} ₽</span>
                    {best.entry.store_url&&<a href={best.entry.store_url} target="_blank" rel="noopener noreferrer" className="best-link">🛒 PS Store</a>}
                  </div>
                )}
                {prices.length>1&&(
                  <div className="all-prices">
                    <button className="toggle-btn" onClick={()=>setExpandedId(isExp?null:g.id)}>
                      {isExp?"▲":"▼"} All prices ({prices.length})
                    </button>
                    {isExp&&(
                      <div className="prices-list">
                        {prices.map(e=>{
                          const isBest=best&&e.id===best.entry.id;
                          return(
                            <div key={e.id} className={`price-row ${isBest?"price-best":""}`}>
                              <span className="price-region">{REGION_NAMES[e.region]||e.region}</span>
                              <span className="price-amount">{formatCur(e.current_price!,e.currency)}</span>
                              <span className="price-rub">≈ {e.rub<1?e.rub.toFixed(2):e.rub.toFixed(0)} ₽</span>
                              {e.store_url&&<a href={e.store_url} target="_blank" rel="noopener noreferrer" className="price-link">🔗</a>}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
                {!best&&<div className="no-price">Price unavailable</div>}
              </div>
            );
          })}
        </div>
      )}
      <style jsx>{`
        .page{max-width:1400px;margin:0 auto;padding:2rem}
        .page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.5rem}
        .title{font-size:2rem;font-weight:800;color:#1a1a2e}
        .subtitle{color:#666;font-size:.95rem}
        .filters{background:#fff;border-radius:16px;padding:1.25rem;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:1.5rem;display:flex;flex-direction:column;gap:1rem}
        .search-input{width:100%;padding:.75rem 1rem;border:2px solid #e0e0e0;border-radius:12px;font-size:1rem}
        .search-input:focus{outline:none;border-color:#6c5ce7}
        .filter-group{display:flex;align-items:center;gap:.75rem;flex-wrap:wrap}
        .filter-label{font-size:.85rem;font-weight:600;color:#666;white-space:nowrap}
        .chip-group{display:flex;gap:.5rem;flex-wrap:wrap}
        .chip{padding:.4rem .9rem;border:2px solid #e0e0e0;border-radius:20px;background:#fff;cursor:pointer;font-size:.82rem;font-weight:600;transition:all .2s;white-space:nowrap}
        .chip:hover{border-color:#6c5ce7}
        .chip-active{background:#6c5ce7;color:#fff;border-color:#6c5ce7}
        .results-count{color:#666;font-size:.9rem;margin-bottom:1rem}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem}
        .card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);transition:transform .2s,box-shadow .2s}
        .card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
        .cover-wrapper{position:relative}
        .cover{width:100%;height:170px;object-fit:cover;display:block}
        .cover-placeholder{width:100%;height:170px;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:3rem}
        .platforms{position:absolute;top:8px;left:8px;display:flex;gap:4px}
        .plat-badge{background:rgba(0,0,0,.7);color:#fff;padding:2px 8px;border-radius:6px;font-size:.7rem;font-weight:700}
        .ps5{background:rgba(0,48,135,.8)}
        .ps4{background:rgba(0,55,155,.7)}
        .disc-badge{position:absolute;top:8px;right:52px;background:#e53e3e;color:#fff;padding:2px 8px;border-radius:6px;font-size:.7rem;font-weight:700}
        .fav-btn{position:absolute;top:8px;right:8px;background:rgba(0,0,0,.5);border:none;border-radius:50%;width:36px;height:36px;font-size:1.2rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}
        .fav-btn:hover{transform:scale(1.15)}
        .fav-active{background:rgba(255,255,255,.9)}
        .game-name{padding:1rem 1rem .5rem;font-size:1.05rem;font-weight:700;color:#1a1a2e;line-height:1.3;min-height:3.2em;overflow:hidden}
        .best-price{margin:.5rem 1rem;padding:.75rem;background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:10px;border:2px solid #4caf50;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
        .best-label{font-size:.75rem;font-weight:600;color:#2e7d32;text-transform:uppercase}
        .best-value{font-size:1.15rem;font-weight:800;color:#1b5e20}
        .best-region{font-size:.8rem;color:#388e3c}
        .best-rub{font-size:.85rem;font-weight:600;color:#2e7d32;margin-left:auto}
        .best-link{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:#1b5e20;color:#fff;text-decoration:none;border-radius:6px;font-size:.8rem;font-weight:600}
        .all-prices{margin:.5rem 1rem 1rem}
        .toggle-btn{width:100%;padding:.5rem;background:#f0f0f0;border:none;border-radius:8px;cursor:pointer;font-size:.85rem;font-weight:600;color:#6c5ce7}
        .prices-list{margin-top:.5rem;display:flex;flex-direction:column;gap:4px}
        .price-row{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;border-radius:8px;background:#f8f9fa;font-size:.82rem}
        .price-best{background:#e8f5e9;border:1px solid #4caf50;font-weight:600}
        .price-region{flex:1}
        .price-amount{font-weight:600;margin-right:.5rem}
        .price-rub{color:#666;min-width:70px;text-align:right}
        .price-link{text-decoration:none;font-size:1rem;margin-left:6px}
        .no-price{margin:.5rem 1rem 1rem;padding:.5rem;background:#f5f5f5;border-radius:8px;text-align:center;color:#999;font-size:.85rem}
        .loading,.empty{text-align:center;padding:4rem 2rem;font-size:1.1rem;color:#666}
        @media(max-width:640px){.page{padding:1rem}.title{font-size:1.5rem}.grid{grid-template-columns:1fr}.filters{padding:1rem}}
      `}</style>
    </div>
  );
}
