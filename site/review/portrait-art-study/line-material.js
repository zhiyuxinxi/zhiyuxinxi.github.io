/* Transparent illustrated ribbons. Geometry remains owned by tree-layout.js. */
window.LineMaterial = (() => {
  const canvas=document.createElement('canvas');canvas.id='line-material';canvas.setAttribute('aria-hidden','true');
  document.querySelector('#viewport').prepend(canvas);
  const gl=canvas.getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:true,preserveDrawingBuffer:true});
  let ready=false,error=null,program,buffer,position,uv,resolution,sampler;const textures={};
  const assets={sageThick:'assets/line-sage-thick.png',sageFine:'assets/line-sage-fine.png',amberThick:'assets/line-amber-thick.png',amberFine:'assets/line-amber-fine.png'};
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
  function setup(){
    if(!gl)throw Error('WebGL is unavailable; illustrated line materials cannot be displayed.');
    program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec2 aPosition;attribute vec2 aUV;uniform vec2 uResolution;varying vec2 vUV;void main(){vec2 p=aPosition/uResolution*2.0-1.0;gl_Position=vec4(p.x,-p.y,0,1);vUV=aUV;}'));
    gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D uTexture;varying vec2 vUV;void main(){gl_FragColor=texture2D(uTexture,vUV);}'));
    gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
    position=gl.getAttribLocation(program,'aPosition');uv=gl.getAttribLocation(program,'aUV');resolution=gl.getUniformLocation(program,'uResolution');sampler=gl.getUniformLocation(program,'uTexture');buffer=gl.createBuffer();
    gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,true);
  }
  async function load(){try{setup();await Promise.all(Object.entries(assets).map(([name,url])=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);gl.generateMipmap(gl.TEXTURE_2D);textures[name]=t;resolve()} ;image.onerror=()=>reject(Error('Missing illustrated line asset: '+url));image.src=url})));ready=true;canvas.dispatchEvent(new CustomEvent('materials-ready'));}catch(e){error=e.message;canvas.dataset.error=error;const message=document.createElement('p');message.setAttribute('role','status');message.className='line-material-error';message.textContent='线条图像暂不可用，请刷新重试。';canvas.after(message);console.error(error)}}
  function mesh(q,start,end){const points=Array.from({length:97},(_,i)=>TreeGeometry.point(q,i/96)),arc=[0];for(let i=1;i<points.length;i++)arc.push(arc[i-1]+Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]));const total=arc.at(-1)||1,vertices=[];
    for(let i=0;i<points.length;i++){const t=arc[i]/total,p=points[i],before=points[Math.max(0,i-1)],after=points[Math.min(points.length-1,i+1)],dx=after[0]-before[0],dy=after[1]-before[1],length=Math.hypot(dx,dy)||1;
      // Smooth width, continuous UVs: no stamped segments or overlapping alpha seams.
      const width=(start*(1-t)+end*t)*(.86+.2*Math.sin(Math.PI*t));
      for(const side of [-1,1])vertices.push(p[0]-dy/length*width*side/2,p[1]+dx/length*width*side/2,t,(side+1)/2);
    }return new Float32Array(vertices);
  }
  function draw(edges,w,h,zoom=1){if(!ready)return false;const dpr=Math.min(devicePixelRatio||1,2.5),cw=Math.round(w*dpr),ch=Math.round(h*dpr);if(canvas.width!==cw||canvas.height!==ch){canvas.width=cw;canvas.height=ch}gl.viewport(0,0,cw,ch);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(program);gl.uniform2f(resolution,w,h);gl.uniform1i(sampler,0);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.enableVertexAttribArray(position);gl.enableVertexAttribArray(uv);gl.vertexAttribPointer(position,2,gl.FLOAT,false,16,0);gl.vertexAttribPointer(uv,2,gl.FLOAT,false,16,8);
    for(const edge of edges){const thick=edge.depth===1,scale=Math.min(1.5,Math.max(.8,Math.sqrt(zoom))),data=mesh(edge.q,(thick?8:edge.preview?3.8:5)*scale,(thick?3.6:1.5)*scale);gl.bufferData(gl.ARRAY_BUFFER,data,gl.DYNAMIC_DRAW);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,textures[(edge.warm?'amber':'sage')+(thick?'Thick':'Fine')]);gl.drawArrays(gl.TRIANGLE_STRIP,0,data.length/4)}return true;
  }
  return {load,draw,status:()=>({ready,error,assets:Object.keys(textures)}),canvas,mesh};
})();
