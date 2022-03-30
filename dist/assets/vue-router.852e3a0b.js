import{s as e,u as t,c as n,d as r,i as o,n as a,e as s,h as c,p as l,f as i,w as u,o as f,g as p,j as h}from"./@vue.160ddf67.js";
/*!
  * vue-router v4.0.10
  * (c) 2021 Eduardo San Martin Morote
  * @license MIT
  */const d="function"==typeof Symbol&&"symbol"==typeof Symbol.toStringTag,m=e=>d?Symbol(e):"_vr_"+e,g=m("rvlm"),v=m("rvd"),y=m("r"),b=m("rl"),w=m("rvl"),E="undefined"!=typeof window;const A=Object.assign;function R(e,t){const n={};for(const r in t){const o=t[r];n[r]=Array.isArray(o)?o.map(e):e(o)}return n}let k=()=>{};const O=/\/$/;function P(e,t,n="/"){let r,o={},a="",s="";const c=t.indexOf("?"),l=t.indexOf("#",c>-1?c:0);return c>-1&&(r=t.slice(0,c),a=t.slice(c+1,l>-1?l:t.length),o=e(a)),l>-1&&(r=r||t.slice(0,l),s=t.slice(l,t.length)),r=function(e,t){if(e.startsWith("/"))return e;if(!e)return t;const n=t.split("/"),r=e.split("/");let o,a,s=n.length-1;for(o=0;o<r.length;o++)if(a=r[o],1!==s&&"."!==a){if(".."!==a)break;s--}return n.slice(0,s).join("/")+"/"+r.slice(o-(o===r.length?1:0)).join("/")}(null!=r?r:t,n),{fullPath:r+(a&&"?")+a+s,path:r,query:o,hash:s}}function x(e,t){return t&&e.toLowerCase().startsWith(t.toLowerCase())?e.slice(t.length)||"/":e}function C(e,t){return(e.aliasOf||e)===(t.aliasOf||t)}function $(e,t){if(Object.keys(e).length!==Object.keys(t).length)return!1;for(let n in e)if(!j(e[n],t[n]))return!1;return!0}function j(e,t){return Array.isArray(e)?S(e,t):Array.isArray(t)?S(t,e):e===t}function S(e,t){return Array.isArray(t)?e.length===t.length&&e.every(((e,n)=>e===t[n])):1===e.length&&e[0]===t}var q,L,_,B;function G(e){if(!e)if(E){const t=document.querySelector("base");e=(e=t&&t.getAttribute("href")||"/").replace(/^\w+:\/\/[^\/]+/,"")}else e="/";return"/"!==e[0]&&"#"!==e[0]&&(e="/"+e),e.replace(O,"")}(L=q||(q={})).pop="pop",L.push="push",(B=_||(_={})).back="back",B.forward="forward",B.unknown="";const M=/^[^#]+#/;function I(e,t){return e.replace(M,"#")+t}const T=()=>({left:window.pageXOffset,top:window.pageYOffset});function U(e){let t;if("el"in e){let n=e.el;const r="string"==typeof n&&n.startsWith("#"),o="string"==typeof n?r?document.getElementById(n.slice(1)):document.querySelector(n):n;if(!o)return;t=function(e,t){const n=document.documentElement.getBoundingClientRect(),r=e.getBoundingClientRect();return{behavior:t.behavior,left:r.left-n.left-(t.left||0),top:r.top-n.top-(t.top||0)}}(o,e)}else t=e;"scrollBehavior"in document.documentElement.style?window.scrollTo(t):window.scrollTo(null!=t.left?t.left:window.pageXOffset,null!=t.top?t.top:window.pageYOffset)}function F(e,t){return(history.state?history.state.position-t:-1)+e}const W=new Map;function D(e,t){const{pathname:n,search:r,hash:o}=t,a=e.indexOf("#");if(a>-1){let t=o.includes(e.slice(a))?e.slice(a).length:1,n=o.slice(t);return"/"!==n[0]&&(n="/"+n),x(n,"")}return x(n,e)+r+o}function V(e,t,n,r=!1,o=!1){return{back:e,current:t,forward:n,replaced:r,position:window.history.length,scroll:o?T():null}}function z(e){const{history:t,location:n}=window;let r={value:D(e,n)},o={value:t.state};function a(r,a,s){const c=e.indexOf("#"),l=c>-1?(n.host&&document.querySelector("base")?e:e.slice(c))+r:location.protocol+"//"+location.host+e+r;try{t[s?"replaceState":"pushState"](a,"",l),o.value=a}catch(i){console.error(i),n[s?"replace":"assign"](l)}}return o.value||a(r.value,{back:null,current:r.value,forward:null,position:t.length-1,replaced:!0,scroll:null},!0),{location:r,state:o,push:function(e,n){const s=A({},o.value,t.state,{forward:e,scroll:T()});a(s.current,s,!0),a(e,A({},V(r.value,e,null),{position:s.position+1},n),!1),r.value=e},replace:function(e,n){a(e,A({},t.state,V(o.value.back,e,o.value.forward,!0),n,{position:o.value.position}),!0),r.value=e}}}function K(e){const t=z(e=G(e)),n=function(e,t,n,r){let o=[],a=[],s=null;const c=({state:a})=>{const c=D(e,location),l=n.value,i=t.value;let u=0;if(a){if(n.value=c,t.value=a,s&&s===l)return void(s=null);u=i?a.position-i.position:0}else r(c);o.forEach((e=>{e(n.value,l,{delta:u,type:q.pop,direction:u?u>0?_.forward:_.back:_.unknown})}))};function l(){const{history:e}=window;e.state&&e.replaceState(A({},e.state,{scroll:T()}),"")}return window.addEventListener("popstate",c),window.addEventListener("beforeunload",l),{pauseListeners:function(){s=n.value},listen:function(e){o.push(e);const t=()=>{const t=o.indexOf(e);t>-1&&o.splice(t,1)};return a.push(t),t},destroy:function(){for(const e of a)e();a=[],window.removeEventListener("popstate",c),window.removeEventListener("beforeunload",l)}}}(e,t.state,t.location,t.replace);const r=A({location:"",base:e,go:function(e,t=!0){t||n.pauseListeners(),history.go(e)},createHref:I.bind(null,e)},t,n);return Object.defineProperty(r,"location",{enumerable:!0,get:()=>t.location.value}),Object.defineProperty(r,"state",{enumerable:!0,get:()=>t.state.value}),r}function H(e){return(e=location.host?e||location.pathname+location.search:"").includes("#")||(e+="#"),K(e)}function Q(e){return"string"==typeof e||"symbol"==typeof e}const X={path:"/",name:void 0,params:{},query:{},hash:"",fullPath:"/",matched:[],meta:{},redirectedFrom:void 0},Y=m("nf");var N,Z;function J(e,t){return A(new Error,{type:e,[Y]:!0},t)}function ee(e,t){return e instanceof Error&&Y in e&&(null==t||!!(e.type&t))}(Z=N||(N={}))[Z.aborted=4]="aborted",Z[Z.cancelled=8]="cancelled",Z[Z.duplicated=16]="duplicated";const te={sensitive:!1,strict:!1,start:!0,end:!0},ne=/[.+*?^${}()[\]/\\]/g;function re(e,t){let n=0;for(;n<e.length&&n<t.length;){const r=t[n]-e[n];if(r)return r;n++}return e.length<t.length?1===e.length&&80===e[0]?-1:1:e.length>t.length?1===t.length&&80===t[0]?1:-1:0}function oe(e,t){let n=0;const r=e.score,o=t.score;for(;n<r.length&&n<o.length;){const e=re(r[n],o[n]);if(e)return e;n++}return o.length-r.length}const ae={type:0,value:""},se=/[a-zA-Z0-9_]/;function ce(e,t,n){const r=function(e,t){const n=A({},te,t);let r=[],o=n.start?"^":"";const a=[];for(const l of e){const e=l.length?[]:[90];n.strict&&!l.length&&(o+="/");for(let t=0;t<l.length;t++){const r=l[t];let s=40+(n.sensitive?.25:0);if(0===r.type)t||(o+="/"),o+=r.value.replace(ne,"\\$&"),s+=40;else if(1===r.type){const{value:e,repeatable:n,optional:i,regexp:u}=r;a.push({name:e,repeatable:n,optional:i});const f=u||"[^/]+?";if("[^/]+?"!==f){s+=10;try{new RegExp(`(${f})`)}catch(c){throw new Error(`Invalid custom RegExp for param "${e}" (${f}): `+c.message)}}let p=n?`((?:${f})(?:/(?:${f}))*)`:`(${f})`;t||(p=i&&l.length<2?`(?:/${p})`:"/"+p),i&&(p+="?"),o+=p,s+=20,i&&(s+=-8),n&&(s+=-20),".*"===f&&(s+=-50)}e.push(s)}r.push(e)}if(n.strict&&n.end){const e=r.length-1;r[e][r[e].length-1]+=.7000000000000001}n.strict||(o+="/?"),n.end?o+="$":n.strict&&(o+="(?:/|$)");const s=new RegExp(o,n.sensitive?"":"i");return{re:s,score:r,keys:a,parse:function(e){const t=e.match(s),n={};if(!t)return null;for(let r=1;r<t.length;r++){const e=t[r]||"",o=a[r-1];n[o.name]=e&&o.repeatable?e.split("/"):e}return n},stringify:function(t){let n="",r=!1;for(const o of e){r&&n.endsWith("/")||(n+="/"),r=!1;for(const e of o)if(0===e.type)n+=e.value;else if(1===e.type){const{value:a,repeatable:s,optional:c}=e,l=a in t?t[a]:"";if(Array.isArray(l)&&!s)throw new Error(`Provided param "${a}" is an array but it is not repeatable (* or + modifiers)`);const i=Array.isArray(l)?l.join("/"):l;if(!i){if(!c)throw new Error(`Missing required param "${a}"`);o.length<2&&(n.endsWith("/")?n=n.slice(0,-1):r=!0)}n+=i}}return n}}}(function(e){if(!e)return[[]];if("/"===e)return[[ae]];if(!e.startsWith("/"))throw new Error(`Invalid path "${e}"`);function t(e){throw new Error(`ERR (${n})/"${i}": ${e}`)}let n=0,r=n;const o=[];let a;function s(){a&&o.push(a),a=[]}let c,l=0,i="",u="";function f(){i&&(0===n?a.push({type:0,value:i}):1===n||2===n||3===n?(a.length>1&&("*"===c||"+"===c)&&t(`A repeatable param (${i}) must be alone in its segment. eg: '/:ids+.`),a.push({type:1,value:i,regexp:u,repeatable:"*"===c||"+"===c,optional:"*"===c||"?"===c})):t("Invalid state to consume buffer"),i="")}function p(){i+=c}for(;l<e.length;)if(c=e[l++],"\\"!==c||2===n)switch(n){case 0:"/"===c?(i&&f(),s()):":"===c?(f(),n=1):p();break;case 4:p(),n=r;break;case 1:"("===c?n=2:se.test(c)?p():(f(),n=0,"*"!==c&&"?"!==c&&"+"!==c&&l--);break;case 2:")"===c?"\\"==u[u.length-1]?u=u.slice(0,-1)+c:n=3:u+=c;break;case 3:f(),n=0,"*"!==c&&"?"!==c&&"+"!==c&&l--,u="";break;default:t("Unknown state")}else r=n,n=4;return 2===n&&t(`Unfinished custom RegExp for param "${i}"`),f(),s(),o}(e.path),n),o=A(r,{record:e,parent:t,children:[],alias:[]});return t&&!o.record.aliasOf==!t.record.aliasOf&&t.children.push(o),o}function le(e,t){const n=[],r=new Map;function o(e,n,r){let c=!r,l=function(e){return{path:e.path,redirect:e.redirect,name:e.name,meta:e.meta||{},aliasOf:void 0,beforeEnter:e.beforeEnter,props:ie(e),children:e.children||[],instances:{},leaveGuards:new Set,updateGuards:new Set,enterCallbacks:{},components:"components"in e?e.components||{}:{default:e.component}}}(e);l.aliasOf=r&&r.record;const i=pe(t,e),u=[l];if("alias"in e){const t="string"==typeof e.alias?[e.alias]:e.alias;for(const e of t)u.push(A({},l,{components:r?r.record.components:l.components,path:e,aliasOf:r?r.record:l}))}let f,p;for(const t of u){let{path:u}=t;if(n&&"/"!==u[0]){let e=n.record.path,r="/"===e[e.length-1]?"":"/";t.path=n.record.path+(u&&r+u)}if(f=ce(t,n,i),r?r.alias.push(f):(p=p||f,p!==f&&p.alias.push(f),c&&e.name&&!ue(f)&&a(e.name)),"children"in l){let e=l.children;for(let t=0;t<e.length;t++)o(e[t],f,r&&r.children[t])}r=r||f,s(f)}return p?()=>{a(p)}:k}function a(e){if(Q(e)){const t=r.get(e);t&&(r.delete(e),n.splice(n.indexOf(t),1),t.children.forEach(a),t.alias.forEach(a))}else{let t=n.indexOf(e);t>-1&&(n.splice(t,1),e.record.name&&r.delete(e.record.name),e.children.forEach(a),e.alias.forEach(a))}}function s(e){let t=0;for(;t<n.length&&oe(e,n[t])>=0;)t++;n.splice(t,0,e),e.record.name&&!ue(e)&&r.set(e.record.name,e)}return t=pe({strict:!1,end:!0,sensitive:!1},t),e.forEach((e=>o(e))),{addRoute:o,resolve:function(e,t){let o,a,s,c={};if("name"in e&&e.name){if(o=r.get(e.name),!o)throw J(1,{location:e});s=o.record.name,c=A(function(e,t){let n={};for(let r of t)r in e&&(n[r]=e[r]);return n}(t.params,o.keys.filter((e=>!e.optional)).map((e=>e.name))),e.params),a=o.stringify(c)}else if("path"in e)a=e.path,o=n.find((e=>e.re.test(a))),o&&(c=o.parse(a),s=o.record.name);else{if(o=t.name?r.get(t.name):n.find((e=>e.re.test(t.path))),!o)throw J(1,{location:e,currentLocation:t});s=o.record.name,c=A({},t.params,e.params),a=o.stringify(c)}const l=[];let i=o;for(;i;)l.unshift(i.record),i=i.parent;return{name:s,path:a,params:c,matched:l,meta:fe(l)}},removeRoute:a,getRoutes:function(){return n},getRecordMatcher:function(e){return r.get(e)}}}function ie(e){const t={},n=e.props||!1;if("component"in e)t.default=n;else for(let r in e.components)t[r]="boolean"==typeof n?n:n[r];return t}function ue(e){for(;e;){if(e.record.aliasOf)return!0;e=e.parent}return!1}function fe(e){return e.reduce(((e,t)=>A(e,t.meta)),{})}function pe(e,t){let n={};for(let r in e)n[r]=r in t?t[r]:e[r];return n}const he=/#/g,de=/&/g,me=/\//g,ge=/=/g,ve=/\?/g,ye=/\+/g,be=/%5B/g,we=/%5D/g,Ee=/%5E/g,Ae=/%60/g,Re=/%7B/g,ke=/%7C/g,Oe=/%7D/g,Pe=/%20/g;function xe(e){return encodeURI(""+e).replace(ke,"|").replace(be,"[").replace(we,"]")}function Ce(e){return xe(e).replace(ye,"%2B").replace(Pe,"+").replace(he,"%23").replace(de,"%26").replace(Ae,"`").replace(Re,"{").replace(Oe,"}").replace(Ee,"^")}function $e(e){return function(e){return xe(e).replace(he,"%23").replace(ve,"%3F")}(e).replace(me,"%2F")}function je(e){try{return decodeURIComponent(""+e)}catch(t){}return""+e}function Se(e){const t={};if(""===e||"?"===e)return t;const n=("?"===e[0]?e.slice(1):e).split("&");for(let r=0;r<n.length;++r){const e=n[r].replace(ye," ");let o=e.indexOf("="),a=je(o<0?e:e.slice(0,o)),s=o<0?null:je(e.slice(o+1));if(a in t){let e=t[a];Array.isArray(e)||(e=t[a]=[e]),e.push(s)}else t[a]=s}return t}function qe(e){let t="";for(let n in e){const r=e[n];if(n=Ce(n).replace(ge,"%3D"),null==r){void 0!==r&&(t+=(t.length?"&":"")+n);continue}(Array.isArray(r)?r.map((e=>e&&Ce(e))):[r&&Ce(r)]).forEach((e=>{void 0!==e&&(t+=(t.length?"&":"")+n,null!=e&&(t+="="+e))}))}return t}function Le(e){const t={};for(let n in e){let r=e[n];void 0!==r&&(t[n]=Array.isArray(r)?r.map((e=>null==e?null:""+e)):null==r?r:""+r)}return t}function _e(){let e=[];return{add:function(t){return e.push(t),()=>{const n=e.indexOf(t);n>-1&&e.splice(n,1)}},list:()=>e,reset:function(){e=[]}}}function Be(e){const t=o(g,{}).value;t&&function(e,t,n){const r=()=>{e[t].delete(n)};f(r),p(r),h((()=>{e[t].add(n)})),e[t].add(n)}(t,"updateGuards",e)}function Ge(e,t,n,r,o){const a=r&&(r.enterCallbacks[o]=r.enterCallbacks[o]||[]);return()=>new Promise(((s,c)=>{const l=e=>{var l;!1===e?c(J(4,{from:n,to:t})):e instanceof Error?c(e):"string"==typeof(l=e)||l&&"object"==typeof l?c(J(2,{from:t,to:e})):(a&&r.enterCallbacks[o]===a&&"function"==typeof e&&a.push(e),s())},i=e.call(r&&r.instances[o],t,n,l);let u=Promise.resolve(i);e.length<3&&(u=u.then(l)),u.catch((e=>c(e)))}))}function Me(e,t,n,r){const o=[];for(const s of e)for(const e in s.components){let c=s.components[e];if("beforeRouteEnter"===t||s.instances[e])if("object"==typeof(a=c)||"displayName"in a||"props"in a||"__vccOpts"in a){const a=(c.__vccOpts||c)[t];a&&o.push(Ge(a,n,r,s,e))}else{let a=c();o.push((()=>a.then((o=>{if(!o)return Promise.reject(new Error(`Couldn't resolve component "${e}" at "${s.path}"`));const a=(c=o).__esModule||d&&"Module"===c[Symbol.toStringTag]?o.default:o;var c;s.components[e]=a;const l=(a.__vccOpts||a)[t];return l&&Ge(l,n,r,s,e)()}))))}}var a;return o}function Ie(e){const r=o(y),a=o(b),s=n((()=>r.resolve(t(e.to)))),c=n((()=>{let{matched:e}=s.value,{length:t}=e;const n=e[t-1];let r=a.matched;if(!n||!r.length)return-1;let o=r.findIndex(C.bind(null,n));if(o>-1)return o;let c=Ue(e[t-2]);return t>1&&Ue(n)===c&&r[r.length-1].path!==c?r.findIndex(C.bind(null,e[t-2])):o})),l=n((()=>c.value>-1&&function(e,t){for(let n in t){let r=t[n],o=e[n];if("string"==typeof r){if(r!==o)return!1}else if(!Array.isArray(o)||o.length!==r.length||r.some(((e,t)=>e!==o[t])))return!1}return!0}(a.params,s.value.params))),i=n((()=>c.value>-1&&c.value===a.matched.length-1&&$(a.params,s.value.params)));return{route:s,href:n((()=>s.value.href)),isActive:l,isExactActive:i,navigate:function(n={}){return function(e){if(e.metaKey||e.altKey||e.ctrlKey||e.shiftKey)return;if(e.defaultPrevented)return;if(void 0!==e.button&&0!==e.button)return;if(e.currentTarget&&e.currentTarget.getAttribute){const t=e.currentTarget.getAttribute("target");if(/\b_blank\b/i.test(t))return}e.preventDefault&&e.preventDefault();return!0}(n)?r[t(e.replace)?"replace":"push"](t(e.to)).catch(k):Promise.resolve()}}}const Te=s({name:"RouterLink",props:{to:{type:[String,Object],required:!0},replace:Boolean,activeClass:String,exactActiveClass:String,custom:Boolean,ariaCurrentValue:{type:String,default:"page"}},useLink:Ie,setup(e,{slots:t}){const a=r(Ie(e)),{options:s}=o(y),l=n((()=>({[Fe(e.activeClass,s.linkActiveClass,"router-link-active")]:a.isActive,[Fe(e.exactActiveClass,s.linkExactActiveClass,"router-link-exact-active")]:a.isExactActive})));return()=>{const n=t.default&&t.default(a);return e.custom?n:c("a",{"aria-current":a.isExactActive?e.ariaCurrentValue:null,href:a.href,onClick:a.navigate,class:l.value},n)}}});function Ue(e){return e?e.aliasOf?e.aliasOf.path:e.path:""}const Fe=(e,t,n)=>null!=e?e:null!=t?t:n;function We(e,t){if(!e)return null;const n=e(t);return 1===n.length?n[0]:n}const De=s({name:"RouterView",inheritAttrs:!1,props:{name:{type:String,default:"default"},route:Object},setup(e,{attrs:t,slots:r}){const a=o(w),s=n((()=>e.route||a.value)),f=o(v,0),p=n((()=>s.value.matched[f]));l(v,f+1),l(g,p),l(w,s);const h=i();return u((()=>[h.value,p.value,e.name]),(([e,t,n],[r,o,a])=>{t&&(t.instances[n]=e,o&&o!==t&&e&&e===r&&(t.leaveGuards.size||(t.leaveGuards=o.leaveGuards),t.updateGuards.size||(t.updateGuards=o.updateGuards))),!e||!t||o&&C(t,o)&&r||(t.enterCallbacks[n]||[]).forEach((t=>t(e)))}),{flush:"post"}),()=>{const n=s.value,o=p.value,a=o&&o.components[e.name],l=e.name;if(!a)return We(r.default,{Component:a,route:n});const i=o.props[e.name],u=i?!0===i?n.params:"function"==typeof i?i(n):i:null,f=c(a,A({},u,t,{onVnodeUnmounted:e=>{e.component.isUnmounted&&(o.instances[l]=null)},ref:h}));return We(r.default,{Component:f,route:n})||f}}});function Ve(o){const s=le(o.routes,o);let c=o.parseQuery||Se,l=o.stringifyQuery||qe,i=o.history;const u=_e(),f=_e(),p=_e(),h=e(X);let d=X;E&&o.scrollBehavior&&"scrollRestoration"in history&&(history.scrollRestoration="manual");const m=R.bind(null,(e=>""+e)),g=R.bind(null,$e),v=R.bind(null,je);function O(e,t){if(t=A({},t||h.value),"string"==typeof e){let n=P(c,e,t.path),r=s.resolve({path:n.path},t),o=i.createHref(n.fullPath);return A(n,r,{params:v(r.params),hash:je(n.hash),redirectedFrom:void 0,href:o})}let n;"path"in e?n=A({},e,{path:P(c,e.path,t.path).path}):(n=A({},e,{params:g(e.params)}),t.params=g(t.params));let r=s.resolve(n,t);const o=e.hash||"";r.params=m(v(r.params));const a=function(e,t){let n=t.query?e(t.query):"";return t.path+(n&&"?")+n+(t.hash||"")}(l,A({},e,{hash:(u=o,xe(u).replace(Re,"{").replace(Oe,"}").replace(Ee,"^")),path:r.path}));var u;let f=i.createHref(a);return A({fullPath:a,hash:o,query:l===qe?Le(e.query):e.query},r,{redirectedFrom:void 0,href:f})}function x(e){return"string"==typeof e?P(c,e,h.value.path):A({},e)}function j(e,t){if(d!==e)return J(8,{from:t,to:e})}function S(e){return _(e)}function L(e){const t=e.matched[e.matched.length-1];if(t&&t.redirect){const{redirect:n}=t;let r="function"==typeof n?n(e):n;return"string"==typeof r&&(r=r.includes("?")||r.includes("#")?r=x(r):{path:r},r.params={}),A({query:e.query,hash:e.hash,params:e.params},r)}}function _(e,t){const n=d=O(e),r=h.value,o=e.state,a=e.force,s=!0===e.replace,c=L(n);if(c)return _(A(x(c),{state:o,force:a,replace:s}),t||n);const i=n;let u;return i.redirectedFrom=t,!a&&function(e,t,n){let r=t.matched.length-1,o=n.matched.length-1;return r>-1&&r===o&&C(t.matched[r],n.matched[o])&&$(t.params,n.params)&&e(t.query)===e(n.query)&&t.hash===n.hash}(l,r,n)&&(u=J(16,{to:i,from:r}),Z(r,r,!0,!1)),(u?Promise.resolve(u):G(i,r)).catch((e=>ee(e)?e:Y(e,i,r))).then((e=>{if(e){if(ee(e,2))return _(A(x(e.to),{state:o,force:a,replace:s}),t||i)}else e=I(i,r,!0,s,o);return M(i,r,e),e}))}function B(e,t){const n=j(e,t);return n?Promise.reject(n):Promise.resolve()}function G(e,t){let n;const[r,o,a]=function(e,t){const n=[],r=[],o=[],a=Math.max(t.matched.length,e.matched.length);for(let s=0;s<a;s++){const a=t.matched[s];a&&(e.matched.find((e=>C(e,a)))?r.push(a):n.push(a));const c=e.matched[s];c&&(t.matched.find((e=>C(e,c)))||o.push(c))}return[n,r,o]}(e,t);n=Me(r.reverse(),"beforeRouteLeave",e,t);for(const c of r)c.leaveGuards.forEach((r=>{n.push(Ge(r,e,t))}));const s=B.bind(null,e,t);return n.push(s),ze(n).then((()=>{n=[];for(const r of u.list())n.push(Ge(r,e,t));return n.push(s),ze(n)})).then((()=>{n=Me(o,"beforeRouteUpdate",e,t);for(const r of o)r.updateGuards.forEach((r=>{n.push(Ge(r,e,t))}));return n.push(s),ze(n)})).then((()=>{n=[];for(const r of e.matched)if(r.beforeEnter&&!t.matched.includes(r))if(Array.isArray(r.beforeEnter))for(const o of r.beforeEnter)n.push(Ge(o,e,t));else n.push(Ge(r.beforeEnter,e,t));return n.push(s),ze(n)})).then((()=>(e.matched.forEach((e=>e.enterCallbacks={})),n=Me(a,"beforeRouteEnter",e,t),n.push(s),ze(n)))).then((()=>{n=[];for(const r of f.list())n.push(Ge(r,e,t));return n.push(s),ze(n)})).catch((e=>ee(e,8)?e:Promise.reject(e)))}function M(e,t,n){for(const r of p.list())r(e,t,n)}function I(e,t,n,r,o){const a=j(e,t);if(a)return a;const s=t===X,c=E?history.state:{};n&&(r||s?i.replace(e.fullPath,A({scroll:s&&c&&c.scroll},o)):i.push(e.fullPath,o)),h.value=e,Z(e,t,n,s),N()}let D;function V(){D=i.listen(((e,t,n)=>{let r=O(e);const o=L(r);if(o)return void _(A(o,{replace:!0}),r).catch(k);d=r;const a=h.value;var s,c;E&&(s=F(a.fullPath,n.delta),c=T(),W.set(s,c)),G(r,a).catch((e=>ee(e,12)?e:ee(e,2)?(_(e.to,r).then((e=>{ee(e,20)&&!n.delta&&n.type===q.pop&&i.go(-1,!1)})).catch(k),Promise.reject()):(n.delta&&i.go(-n.delta,!1),Y(e,r,a)))).then((e=>{(e=e||I(r,a,!1))&&(n.delta?i.go(-n.delta,!1):n.type===q.pop&&ee(e,20)&&i.go(-1,!1)),M(r,a,e)})).catch(k)}))}let z,K=_e(),H=_e();function Y(e,t,n){N(e);const r=H.list();return r.length?r.forEach((r=>r(e,t,n))):console.error(e),Promise.reject(e)}function N(e){z||(z=!0,V(),K.list().forEach((([t,n])=>e?n(e):t())),K.reset())}function Z(e,t,n,r){const{scrollBehavior:s}=o;if(!E||!s)return Promise.resolve();let c=!n&&function(e){const t=W.get(e);return W.delete(e),t}(F(e.fullPath,0))||(r||!n)&&history.state&&history.state.scroll||null;return a().then((()=>s(e,t,c))).then((e=>e&&U(e))).catch((n=>Y(n,e,t)))}const te=e=>i.go(e);let ne;const re=new Set;return{currentRoute:h,addRoute:function(e,t){let n,r;return Q(e)?(n=s.getRecordMatcher(e),r=t):r=e,s.addRoute(r,n)},removeRoute:function(e){let t=s.getRecordMatcher(e);t&&s.removeRoute(t)},hasRoute:function(e){return!!s.getRecordMatcher(e)},getRoutes:function(){return s.getRoutes().map((e=>e.record))},resolve:O,options:o,push:S,replace:function(e){return S(A(x(e),{replace:!0}))},go:te,back:()=>te(-1),forward:()=>te(1),beforeEach:u.add,beforeResolve:f.add,afterEach:p.add,onError:H.add,isReady:function(){return z&&h.value!==X?Promise.resolve():new Promise(((e,t)=>{K.add([e,t])}))},install(e){e.component("RouterLink",Te),e.component("RouterView",De),e.config.globalProperties.$router=this,Object.defineProperty(e.config.globalProperties,"$route",{enumerable:!0,get:()=>t(h)}),E&&!ne&&h.value===X&&(ne=!0,S(i.location).catch((e=>{})));const o={};for(let t in X)o[t]=n((()=>h.value[t]));e.provide(y,this),e.provide(b,r(o)),e.provide(w,h);let a=e.unmount;re.add(e),e.unmount=function(){re.delete(e),re.size<1&&(D(),h.value=X,ne=!1,z=!1),a()}}}}function ze(e){return e.reduce(((e,t)=>e.then((()=>t()))),Promise.resolve())}function Ke(){return o(y)}function He(){return o(b)}export{He as a,H as b,Ve as c,Be as o,Ke as u};
