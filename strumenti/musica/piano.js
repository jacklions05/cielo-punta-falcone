/* ---------- pianoforte: suoni costruiti nella pagina, nessun campione registrato ----------
   Ogni tasto è la somma delle sue armoniche, come una corda vera:
   - le armoniche sono un po' "stonate" verso l'alto (inarmonicità: f_n = n·f0·√(1+B·n²)), che è ciò che fa suonare un piano come un piano;
   - due corde per nota, accordate a pochi centesimi di distanza: battono piano tra loro e il suono "vive";
   - ogni armonica si spegne prima delle più basse, e in due tempi (un colpo iniziale che cala in fretta, poi una coda lunga);
   - un piccolo colpo di martelletto all'attacco.
   Si preparano una volta sola 28 tasti (uno ogni tre semitoni) e le note in mezzo si ottengono cambiando di poco la velocità di lettura. */
const PIANO={buf:null,keys:[],sr:0,pronto:null};
function pianoPrepara(){if(PIANO.pronto)return PIANO.pronto;
  const sr=32000,keys=[];for(let m=24;m<=105;m+=3)keys.push(m);const rn=rngDa(4242),buf=[];
  const lun=m=>m<45?7:m<66?5.5:m<84?3.8:2.4;
  const tasto=m=>{const L=Math.round(lun(m)*sr),x=new Float32Array(L),f0=mtof(m),B=1.2e-4*Math.pow(2,(m-60)/16);
    const tf=1.25*Math.pow(2,-(m-24)/30),ts=tf*(m<50?5.5:4.2),parz=[];let norm=0; // costanti di decadimento: colpo e coda
    for(let n=1;n<=24;n++){const f=n*f0*Math.sqrt(1+B*n*n);if(f>Math.min(9000,sr*.45))break;
      const a=(Math.abs(Math.sin(Math.PI*n/7.3))+.08)/Math.pow(n,m<48?.8:1.05)*(n===1&&m<40?.6:1);parz.push([n,f,a]);norm+=a*a}
    norm=1/Math.sqrt(norm)*(m<40?1.25:m>90?.8:1);
    const att=Math.round(.0025*sr);
    for(const [n,f,a] of parz)for(const dc of [-1,1]){ // due corde, un filo scordate tra loro
      const w=2*Math.PI*f*Math.pow(2,(dc*(.6+rn()*.8)+(rn()-.5)*.4)/1200)/sr,k=1/(1+.22*(n-1)+.0002*f),A=a*norm*.25;
      const r1=Math.exp(-1/(sr*tf*k)),r2=Math.exp(-1/(sr*ts*k)),c2=2*Math.cos(w);let y1=Math.sin(rn()*6.283),y0=Math.sin(Math.asin(y1)-w),e1=A*.68,e2=A*.32;
      for(let i=0;i<L;i++){const y=c2*y1-y0;y0=y1;y1=y;const e=e1+e2;x[i]+=y*e*(i<att?i/att:1);e1*=r1;e2*=r2;if(e<A*2e-4)break}} // oscillatore per ricorrenza: niente seni da calcolare
    const H=Math.round(.06*sr);let lp=0;const fc=Math.min(.9,2*Math.PI*Math.min(4000,f0*3+300)/sr); // il martelletto: un soffio breve, filtrato
    for(let i=0;i<H;i++){lp+=fc*((rn()*2-1)-lp);x[i]+=lp*.5*norm*Math.exp(-i/(sr*.008))}
    for(let i=0;i<400;i++)x[L-1-i]*=i/400; // niente scatti in coda
    return x};
  return PIANO.pronto=new Promise(ok=>{let ki=0;const passo=()=>{const t0=performance.now();
      while(ki<keys.length&&performance.now()-t0<25)buf.push(tasto(keys[ki++])); // a pezzetti, per non bloccare la pagina
      if(ki<keys.length)setTimeout(passo,0);else{PIANO.keys=keys;PIANO.sr=sr;PIANO.buf=buf;ok(true)}};passo()})}
/* suona una nota: m = tasto MIDI, t = quando, du = quanto resta abbassato (pedale compreso), v = forza 1–127 */
function pianoNota(c,dest,m,t,du,v){if(!PIANO.buf)return;let ki=Math.round((m-24)/3);ki=Math.max(0,Math.min(PIANO.keys.length-1,ki));
  if(!PIANO.ab)PIANO.ab=[];if(!PIANO.ab[ki]||PIANO.ab[ki].ctx!==c){const x=PIANO.buf[ki],b=c.createBuffer(1,x.length,PIANO.sr);b.getChannelData(0).set(x);b.ctx=c;PIANO.ab[ki]=b}
  const s=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain(),f0=mtof(m),u=v/127;
  s.buffer=PIANO.ab[ki];s.playbackRate.value=Math.pow(2,(m-PIANO.keys[ki])/12);
  f.type='lowpass';f.Q.value=.4;f.frequency.value=Math.min(16000,f0*(1.6+u*u*9)+500); // più forte = più brillante, come il feltro del martelletto
  const A=.55*Math.pow(u,1.7);g.gain.setValueAtTime(A,t);const fine=t+Math.max(.06,du),sm=m>=89?.35:.07; // le note più acute non hanno smorzatori
  g.gain.setTargetAtTime(0,fine,sm);
  let n=g;if(c.createStereoPanner){const p=c.createStereoPanner();p.pan.value=Math.max(-.5,Math.min(.5,(m-64)/50));g.connect(p);n=p}
  s.connect(f);f.connect(g);n.connect(dest);s.start(t);s.stop(Math.min(t+s.buffer.duration/s.playbackRate.value,fine+sm*6))}
function decodBrano(b64){const s=atob(b64),N=[];let i=0,t=0;const vr=()=>{let x=0,k=0,y;do{y=s.charCodeAt(i++);x|=(y&127)<<k;k+=7}while(y&128);return x};
  while(i<s.length){t+=vr();const du=vr();N.push([t/100,du/100,s.charCodeAt(i++),s.charCodeAt(i++)])}return N}
