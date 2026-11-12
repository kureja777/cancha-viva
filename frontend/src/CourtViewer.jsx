import React,{useEffect,useRef,useState} from 'react';
import * as T from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

// Paint markings into one surface so they stay sharp while orbiting.
function surface(sport,south){
  const canvas=document.createElement('canvas');canvas.width=1536;canvas.height=960;
  const c=canvas.getContext('2d');c.scale(96,96);c.translate(8,5);
  const fill=(color,x,z,w,h)=>{c.fillStyle=color;c.fillRect(x,z,w,h)};
  const path=(pts)=>{c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke()};
  const arc=(x,y,r,a=0,b=Math.PI*2)=>{c.beginPath();c.arc(x,y,r,a,b);c.stroke()};
  const football=sport==='football',basket=sport==='basket';
  fill(football?'#32745a':basket?'#38697b':'#43969a',-8,-5,16,10);
  if(football){
    for(let i=0;i<12;i++)fill((south?['#60975b','#548b52']:['#4e9568','#458a60'])[i%2],-7.4+i*14.8/12,-4.45,14.8/12,8.9);
  }else if(basket){
    for(let j=0;j<30;j++){fill(['#dbab76','#d5a372','#dfb382'][j%3],-7.4,-4.45+j*8.9/30,14.8,8.9/30+.003);
      for(let i=0;i<3;i++)fill('#c79768',-7+(j%3)*1.45+i*4.8,-4.45+j*8.9/30,.014,8.9/30);}
  }else fill('#db906b',-7.4,-4.45,14.8,8.9);
  c.strokeStyle='#fff8e6';c.lineWidth=.055;c.lineJoin='round';
  c.strokeRect(-7.4,-4.45,14.8,8.9);path([[0,-4.45],[0,4.45]]);
  if(football||basket)arc(0,0,football?1.25:1.02);
  if(football){for(const d of [-1,1]){
    for(const [depth,width] of [[2.05,4.55],[.83,2.55]])path([[d*7.4,-width/2],[d*(7.4-depth),-width/2],[d*(7.4-depth),width/2],[d*7.4,width/2]]);
    c.beginPath();c.arc(d*5.9,0,.088,0,2*Math.PI);c.fillStyle=c.strokeStyle;c.fill();
  }}else if(basket){for(const d of [-1,1]){
    fill('#ae7659',d<0?-7.38:4.6,-1.16,2.78,2.32);c.strokeRect(d<0?-7.38:4.6,-1.16,2.78,2.32);
    arc(d*4.6,0,1.16);arc(d*6.7,0,3.35,d<0?-Math.PI/2:Math.PI/2,d<0?Math.PI/2:Math.PI*1.5);
    for(const y of [-3.35,3.35])path([[d*7.4,y],[d*6.7,y]]);
  }}else for(const d of [-1,1])path([[d*2.5,-4.45],[d*2.5,4.45]]);
  const tex=new T.CanvasTexture(canvas);tex.colorSpace=T.SRGBColorSpace;return tex;
}

function buildCourt(scene,court){
  const sport=court.deporte==='Básquet'?'basket':court.deporte==='Vóley'?'volley':'football';
  const cache=new Map(),geo=new T.BoxGeometry(1,1,1),pieces=new Map(),net=[];
  const mat=color=>{if(!cache.has(color))cache.set(color,new T.MeshStandardMaterial({color,roughness:.86}));return cache.get(color)};
  function box(x,y,z,w,h,d,color){if(!pieces.has(color))pieces.set(color,[]);pieces.get(color).push([x,y,z,w,h,d]);}
  const wire=(a,b)=>net.push(...a,...b);
  box(0,-.43,0,20,.65,13.8,'#667c70');box(0,-.095,0,20.12,.12,13.92,'#aabba9');
  box(0,-.006,0,17.7,.07,10.8,'#708981');
  const tex=surface(sport,court.nombre==='Arena Sur');
  const pitch=new T.Mesh(new T.PlaneGeometry(16,10),new T.MeshStandardMaterial({map:tex,roughness:.94}));
  pitch.rotation.x=-Math.PI/2;pitch.position.y=.035;pitch.receiveShadow=true;scene.add(pitch);
  for(const d of [-1,1]){
    // Low stands along the far touchline leave the near side open to the camera.
    for(let j=0;j<2;j++){
      const z=-5.68-j*.54;box(d*3.6,.17+j*.18,z,5.8,.34+j*.36,.55,'#d1d3c0');
      for(let i=0;i<9;i++)box(d*3.6-2.42+i*.6,.38+j*.36,z,.48,.1,.37,i%3===0?'#deb278':'#456e64');
    }
    if(sport==='football'){
      const x=d*7.42,back=d*8.13;
      for(const z of [-1.09,1.09]){
        box(x,.61,z,.075,1.16,.075,'#f7f4df');box((x+back)/2,1.17,z,.78,.06,.06,'#e6e8d5');
        box(back,.6,z,.045,1.14,.045,'#e6e8d5');
        for(let j=0;j<=6;j++)wire([x,.08+j*.18,z],[back,.08+j*.18,z]);
      }
      box(x,1.18,0,.08,.08,2.25,'#fff9e6');
      for(let i=0;i<=12;i++){const z=-1.09+i*2.18/12;wire([back,.07,z],[back,1.17,z]);wire([back,1.17,z],[x,1.17,z]);}
      for(let j=0;j<=6;j++)wire([back,.08+j*.18,-1.09],[back,.08+j*.18,1.09]);
    }else if(sport==='basket'){
      box(d*7.91,1.1,0,.13,2.13,.13,'#374e50');box(d*7.39,2.12,0,1.15,.1,.1,'#374e50');
      box(d*6.86,2.15,0,.085,1.05,1.65,'#eee9d7');
      const hoop=new T.Mesh(new T.TorusGeometry(.28,.04,8,36),mat('#c95431'));hoop.rotation.x=Math.PI/2;hoop.position.set(d*6.52,1.94,0);scene.add(hoop);
      for(let i=0;i<12;i++){const a=i*Math.PI/6;wire([d*6.52+.28*Math.cos(a),1.93,.28*Math.sin(a)],[d*6.52+.17*Math.cos(a+.28),1.59,.17*Math.sin(a+.28)]);}
    }else box(0,.9,d*4.66,.11,1.76,.11,'#265b70');
  }
  if(sport==='volley'){box(0,1.76,0,.055,.09,9.35,'#fff8e4');for(let i=0;i<=52;i++){const z=-4.62+i*9.24/52;wire([0,1.08,z],[0,1.73,z]);}
    for(let j=0;j<=4;j++)wire([0,1.08+j*.16,-4.62],[0,1.08+j*.16,4.62]);}
  scene.add(new T.LineSegments(new T.BufferGeometry().setAttribute('position',new T.Float32BufferAttribute(net,3)),new T.LineBasicMaterial({color:sport==='volley'?'#334a4a':'#e6eada'})));
  const m=new T.Matrix4();for(const [color,items] of pieces){const mesh=new T.InstancedMesh(geo,mat(color),items.length);items.forEach(([x,y,z,w,h,d],i)=>{m.makeScale(w,h,d);m.setPosition(x,y,z);mesh.setMatrixAt(i,m)});mesh.castShadow=mesh.receiveShadow=true;scene.add(mesh);}
  const ball=new T.Mesh(new T.SphereGeometry(.22,20,14),mat(sport==='basket'?'#db7839':sport==='volley'?'#f8d467':'#fff2d6'));ball.castShadow=true;scene.add(ball);
  if(sport==='football'){const patch=new T.CircleGeometry(.065,5);for(const axis of [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]){
    const mark=new T.Mesh(patch,mat('#354340')),n=new T.Vector3(...axis);mark.position.copy(n).multiplyScalar(.217);mark.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),n);ball.add(mark);}}
  return {tex,update(t){const phase=t*.78;ball.rotation.z=-12*Math.sin(phase);ball.position.set(3.7*Math.sin(phase),.265+(sport==='volley'?2.6*Math.cos(phase)**2:sport==='basket'?1.12*Math.abs(Math.sin(t*2.4)):.08*Math.abs(Math.sin(t*3))),1.4+.7*Math.sin(phase));}};
}

export default function CourtViewer({court}){
  const host=useRef(),reset=useRef(),playing=useRef(false);
  const [motion,setMotion]=useState(()=>!window.matchMedia('(prefers-reduced-motion: reduce)').matches),[err,setErr]=useState(false);
  useEffect(()=>{playing.current=motion},[motion]);
  useEffect(()=>{let renderer,controls,observer,frame,texture;const el=host.current,scene=new T.Scene();let alive=true;
    function cleanup(){alive=false;cancelAnimationFrame(frame);observer?.disconnect();controls?.dispose();texture?.dispose();scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();if(o.isInstancedMesh)o.dispose();if(o.isLight)o.shadow?.dispose()});renderer?.dispose();renderer?.forceContextLoss();renderer?.domElement.remove();reset.current=null;}
    try{
      setErr(false);scene.background=new T.Color('#e5eae1');scene.fog=new T.FogExp2('#e5eae1',.015);
      renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.75));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;el.appendChild(renderer.domElement);
      scene.add(new T.HemisphereLight('#fff5da','#a9c0b8',1.9));
      const sun=new T.DirectionalLight('#fff0d4',2.25);sun.position.set(-8,16,7);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-16,right:16,top:16,bottom:-16});sun.shadow.camera.updateProjectionMatrix();sun.shadow.normalBias=.035;scene.add(sun);
      const floor=new T.Mesh(new T.PlaneGeometry(240,240),new T.MeshStandardMaterial({color:'#cdd8c9'}));floor.rotation.x=-Math.PI/2;floor.position.y=-.77;floor.receiveShadow=true;scene.add(floor);
      const model=buildCourt(scene,court);texture=model.tex;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
      const cam=new T.PerspectiveCamera(36,1,.1,240);controls=new OrbitControls(cam,renderer.domElement);controls.enablePan=false;controls.enableDamping=true;controls.minPolarAngle=.15;controls.maxPolarAngle=1.38;controls.minDistance=10;controls.autoRotateSpeed=.65;
      reset.current=()=>{const dist=Math.max(25,35/Math.max(.5,cam.aspect));controls.maxDistance=Math.max(56,dist*1.45);controls.target.set(0,0,0);cam.position.set(.62,.72,.94).normalize().multiplyScalar(dist);controls.update();};
      let lastAspect=0;function resize(){const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;cam.aspect=w/h;cam.updateProjectionMatrix();renderer.setSize(w,h);if(!lastAspect||Math.abs(lastAspect-cam.aspect)>.3)reset.current();lastAspect=cam.aspect;}
      resize();observer=new ResizeObserver(resize);observer.observe(el);let time=0,last=performance.now();
      function draw(now){if(!alive)return;const dt=Math.min(.05,(now-last)/1000);last=now;controls.autoRotate=playing.current;if(playing.current)time+=dt;controls.update(dt);model.update(time);renderer.render(scene,cam);frame=requestAnimationFrame(draw);}draw(last);
    }catch{cleanup();setErr(true);}
    return ()=>{if(alive)cleanup()};
  },[court.id]);
  return <><div className="viewer" ref={host} aria-label={'Vista tridimensional de '+court.nombre}/>{err?<p role="alert">No se pudo iniciar WebGL. El catálogo y las reservas siguen disponibles.</p>:<><div className="filters" style={{marginTop:12}}><button type="button" aria-pressed={motion} onClick={()=>setMotion(v=>!v)}>{motion?'Pausar animación':'Animar cancha'}</button><button type="button" onClick={()=>reset.current?.()}>Restablecer vista</button></div><p className="muted">Arrastra para girar · Usa la rueda o dos dedos para acercar</p></>}</>;
}
