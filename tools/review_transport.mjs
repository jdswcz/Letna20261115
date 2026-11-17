// Private image-review transport used by the analysis. No private key belongs in Git.
import fs from 'node:fs';
import crypto from 'node:crypto';
const helpers = new Function("\nconst P=(1n<<255n)-19n;\nconst mod=x=>((x%P)+P)%P;\nfunction power(a,n){let r=1n;for(a=mod(a);n;n>>=1n,a=mod(a*a))if(n&1n)r=mod(r*a);return r;}\nfunction leNum(a){let x=0n;for(let i=a.length-1;i>=0;i--)x=(x<<8n)|BigInt(a[i]);return x;}\nfunction leBytes(x,n){let a=new Uint8Array(n);for(let i=0;i<n;i++,x>>=8n)a[i]=Number(x&255n);return a;}\nfunction x25519(privateKey,publicKey){\n let k=new Uint8Array(privateKey),u=new Uint8Array(publicKey);\n k[0]&=248;k[31]=(k[31]&127)|64;u[31]&=127;\n const scalar=leNum(k),x1=leNum(u);let x2=1n,z2=0n,x3=x1,z3=1n,swap=0n;\n for(let t=254;t>=0;t--){let bit=(scalar>>BigInt(t))&1n;swap^=bit;\n if(swap){[x2,x3]=[x3,x2];[z2,z3]=[z3,z2];}swap=bit;\n let a=mod(x2+z2),aa=mod(a*a),b=mod(x2-z2),bb=mod(b*b),e=mod(aa-bb);\n let c=mod(x3+z3),d=mod(x3-z3),da=mod(d*a),cb=mod(c*b);\n x3=mod((da+cb)**2n);z3=mod(x1*(da-cb)**2n);x2=mod(aa*bb);z2=mod(e*(aa+121665n*e));\n }if(swap){[x2,x3]=[x3,x2];[z2,z3]=[z3,z2];}\n return leBytes(mod(x2*power(z2,P-2n)),32);\n}\nfunction sha256(input){\n const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];\n const ro=(x,n)=>(x>>>n)|(x<<(32-n));\n const size=Math.ceil((input.length+9)/64)*64,buf=new Uint8Array(size);buf.set(input);buf[input.length]=128;\n let bits=BigInt(input.length)*8n;for(let i=0;i<8;i++){buf[size-1-i]=Number(bits&255n);bits>>=8n;}\n let h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],w=new Uint32Array(64);\n for(let p=0;p<size;p+=64){for(let t=0;t<16;t++)w[t]=(buf[p+4*t]<<24)|(buf[p+4*t+1]<<16)|(buf[p+4*t+2]<<8)|buf[p+4*t+3];\n for(let t=16;t<64;t++){let a=w[t-15],b=w[t-2];w[t]=(w[t-16]+(ro(a,7)^ro(a,18)^(a>>>3))+w[t-7]+(ro(b,17)^ro(b,19)^(b>>>10)))>>>0;}\n let [a,b,c,d,e,f,g,k]=h;\n for(let t=0;t<64;t++){let t1=(k+(ro(e,6)^ro(e,11)^ro(e,25))+((e&f)^(~e&g))+K[t]+w[t])>>>0,t2=((ro(a,2)^ro(a,13)^ro(a,22))+((a&b)^(a&c)^(b&c)))>>>0;k=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}\n h=[a,b,c,d,e,f,g,k].map((x,i)=>(x+h[i])>>>0);\n }return new Uint8Array(h.flatMap(x=>[(x>>>24)&255,(x>>>16)&255,(x>>>8)&255,x&255]));\n}\nfunction chacha(key,nonce,bytes){\n const word=(b,i)=>(b[i]|(b[i+1]<<8)|(b[i+2]<<16)|(b[i+3]<<24))>>>0,rot=(v,n)=>(v<<n)|(v>>>(32-n));\n let state=new Uint32Array([0x61707865,0x3320646e,0x79622d32,0x6b206574,...Array.from({length:8},(_,i)=>word(key,4*i)),...Array.from({length:4},(_,i)=>word(nonce,4*i))]),out=new Uint8Array(bytes.length);\n function qr(s,a,b,c,d){s[a]+=s[b];s[d]=rot(s[d]^s[a],16);s[c]+=s[d];s[b]=rot(s[b]^s[c],12);s[a]+=s[b];s[d]=rot(s[d]^s[a],8);s[c]+=s[d];s[b]=rot(s[b]^s[c],7);}\n for(let p=0;p<bytes.length;p+=64){let s=new Uint32Array(state);for(let j=0;j<10;j++){qr(s,0,4,8,12);qr(s,1,5,9,13);qr(s,2,6,10,14);qr(s,3,7,11,15);qr(s,0,5,10,15);qr(s,1,6,11,12);qr(s,2,7,8,13);qr(s,3,4,9,14);}\n for(let i=0;i<16;i++){let w=(s[i]+state[i])>>>0;for(let b=0;b<4&&p+i*4+b<bytes.length;b++)out[p+i*4+b]=bytes[p+i*4+b]^((w>>>(b*8))&255);}\n state[12]=(state[12]+1)>>>0;if(state[12]===0)state[13]=(state[13]+1)>>>0;\n }return out;\n}\nconst chars=\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/\";\nfunction b64(b){let s=\"\";for(let i=0;i<b.length;i+=3){let a=b[i],c=b[i+1]??0,d=b[i+2]??0,n=(a<<16)|(c<<8)|d;s+=chars[(n>>>18)&63]+chars[(n>>>12)&63]+(i+1<b.length?chars[(n>>>6)&63]:\"=\")+(i+2<b.length?chars[n&63]:\"=\");}return s;}\nfunction unb64(s){let clean=s.replace(/[^A-Za-z0-9+/=]/g,\"\"),r=[];for(let i=0;i<clean.length;i+=4){let n=(chars.indexOf(clean[i])<<18)|(chars.indexOf(clean[i+1])<<12)|((chars.indexOf(clean[i+2])&63)<<6)|(chars.indexOf(clean[i+3])&63);r.push((n>>>16)&255);if(clean[i+2]!==\"=\")r.push((n>>>8)&255);if(clean[i+3]!==\"=\")r.push(n&255);}return new Uint8Array(r);}\nconst hex=b=>Array.from(b,v=>v.toString(16).padStart(2,\"0\")).join(\"\");\nconst fromhex=s=>new Uint8Array(s.match(/../g).map(x=>parseInt(x,16)));\nreturn {x25519,sha256,chacha,b64,unb64,hex,fromhex};\n")();
if (process.argv[2] === "self-test") {
  const b=new Uint8Array(32);b[0]=9;
  if (helpers.hex(helpers.sha256(new Uint8Array([97,98,99]))) !==
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") throw Error("SHA256");
  if (helpers.hex(helpers.x25519(helpers.fromhex(
      "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"),b)) !==
      "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a") throw Error("X25519");
  for (const n of [0,1,55,56,64,1000,220730,669729]) {
    const bytes=crypto.randomBytes(n);
    if (helpers.hex(helpers.sha256(bytes))!==crypto.createHash("sha256").update(bytes).digest("hex"))
      throw Error("SHA256 randomized "+n);
    if (Buffer.from(helpers.unb64(helpers.b64(bytes))).compare(bytes))throw Error("Base64");
  }
  console.log("Review transport self-tests passed");
} else if(process.argv[2] === "keygen") {
  const key=crypto.randomBytes(32),b=new Uint8Array(32);b[0]=9;
  fs.writeFileSync(process.argv[3],key.toString("base64"),{mode:0o600});
  console.log(helpers.b64(helpers.x25519(key,b)));
} else if(process.argv[2] === "decrypt") {
  const log=fs.readFileSync(process.argv[3],"utf8");
  const privateKey=Buffer.from(fs.readFileSync(process.argv[4],"utf8").trim(),"base64");
  const out=process.argv[5];fs.mkdirSync(out,{recursive:true});
  let buffer="";
  for (const line of log.split("\n")) {
    const s=line.replace(/^\d{4}-\d\d-\d\dT\S+\s/,"");
    if(s.startsWith("REVIEW_BEGIN "))buffer="";
    else if(s.startsWith("REVIEW_PART "))buffer+=s.slice(12);
    else if(s.startsWith("REVIEW_END ")) {
      const e=JSON.parse(buffer);
      const key=helpers.sha256(helpers.x25519(privateKey,helpers.unb64(e.ephemeral_public_key)));
      const bytes=helpers.chacha(key,helpers.unb64(e.nonce),helpers.unb64(e.ciphertext));
      if(helpers.hex(helpers.sha256(bytes))!==e.preview_sha256)throw Error("Checksum mismatch: "+e.id);
      fs.writeFileSync(out+"/"+e.id.replace(/[^a-zA-Z0-9_-]/g,"_")+".jpg",bytes);
    }
  }
} else {
  console.log("Usage: node tools/review_transport.mjs self-test | keygen private-key-file | decrypt job.log private-key-file private_downloads");
}
