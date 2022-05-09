import{g as e}from"./vue-i18n.3f148863.js";
/*!
  * @intlify/shared v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */const t="undefined"!=typeof window;const n=/\{([0-9a-zA-Z]+)\}/g;function r(e,...t){return 1===t.length&&x(t[0])&&(t=t[0]),t&&t.hasOwnProperty||(t={}),e.replace(n,((e,n)=>t.hasOwnProperty(n)?t[n]:""))}const o="function"==typeof Symbol&&"symbol"==typeof Symbol.toStringTag,s=(e,t,n)=>a({l:e,k:t,s:n}),a=e=>JSON.stringify(e).replace(/\u2028/g,"\\u2028").replace(/\u2029/g,"\\u2029").replace(/\u0027/g,"\\u0027"),c=e=>"number"==typeof e&&isFinite(e),l=e=>"[object Date]"===T(e),u=e=>"[object RegExp]"===T(e),i=e=>_(e)&&0===Object.keys(e).length;function f(e,t){"undefined"!=typeof console&&(console.warn("[intlify] "+e),t&&console.warn(t.stack))}const p=Object.assign;let m;function d(e){return e.replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&apos;")}const h=Object.prototype.hasOwnProperty;const g=Array.isArray,k=e=>"function"==typeof e,b=e=>"string"==typeof e,y=e=>"boolean"==typeof e,x=e=>null!==e&&"object"==typeof e,L=Object.prototype.toString,T=e=>L.call(e),_=e=>"[object Object]"===T(e),w=e=>null==e?"":g(e)||_(e)&&e.toString===L?JSON.stringify(e,null,2):String(e);var C=Object.freeze({__proto__:null,[Symbol.toStringTag]:"Module",assign:p,createEmitter:function(){const e=new Map;return{events:e,on(t,n){const r=e.get(t);r&&r.push(n)||e.set(t,[n])},off(t,n){const r=e.get(t);r&&r.splice(r.indexOf(n)>>>0,1)},emit(t,n){(e.get(t)||[]).slice().map((e=>e(n))),(e.get("*")||[]).slice().map((e=>e(t,n)))}}},escapeHtml:d,format:r,friendlyJSONstringify:a,generateCodeFrame:function(e,t=0,n=e.length){const r=e.split(/\r?\n/);let o=0;const s=[];for(let a=0;a<r.length;a++)if(o+=r[a].length+1,o>=t){for(let e=a-2;e<=a+2||n>o;e++){if(e<0||e>=r.length)continue;const c=e+1;s.push(`${c}${" ".repeat(3-String(c).length)}|  ${r[e]}`);const l=r[e].length;if(e===a){const e=t-(o-l)+1,r=Math.max(1,n>o?l-e:n-t);s.push("   |  "+" ".repeat(e)+"^".repeat(r))}else if(e>a){if(n>o){const e=Math.max(Math.min(n-o,l),1);s.push("   |  "+"^".repeat(e))}o+=l+1}}break}return s.join("\n")},generateFormatCacheKey:s,getGlobalThis:()=>m||(m="undefined"!=typeof globalThis?globalThis:"undefined"!=typeof self?self:"undefined"!=typeof window?window:"undefined"!=typeof global?global:{}),hasOwn:function(e,t){return h.call(e,t)},inBrowser:t,isArray:g,isBoolean:y,isDate:l,isEmptyObject:i,isFunction:k,isNumber:c,isObject:x,isPlainObject:_,isPromise:e=>x(e)&&k(e.then)&&k(e.catch),isRegExp:u,isString:b,isSymbol:e=>"symbol"==typeof e,makeSymbol:e=>o?Symbol(e):e,mark:undefined,measure:undefined,objectToString:L,toDisplayString:w,toTypeString:T,warn:f});
/*!
  * @intlify/message-resolver v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */const v=Object.prototype.hasOwnProperty;function S(e,t){return v.call(e,t)}const O=e=>null!==e&&"object"==typeof e,P=[];P[0]={w:[0],i:[3,0],"[":[4],o:[7]},P[1]={w:[1],".":[2],"[":[4],o:[7]},P[2]={w:[2],i:[3,0],0:[3,0]},P[3]={i:[3,0],0:[3,0],w:[1,1],".":[2,1],"[":[4,1],o:[7,1]},P[4]={"'":[5,0],'"':[6,0],"[":[4,2],"]":[1,3],o:8,l:[4,0]},P[5]={"'":[4,0],o:8,l:[5,0]},P[6]={'"':[4,0],o:8,l:[6,0]};const F=/^\s?(?:true|false|-?[\d.]+|'[^']*'|"[^"]*")\s?$/;function N(e){if(null==e)return"o";switch(e.charCodeAt(0)){case 91:case 93:case 46:case 34:case 39:return e;case 95:case 36:case 45:return"i";case 9:case 10:case 13:case 160:case 65279:case 8232:case 8233:return"w"}return"i"}function $(e){const t=e.trim();return("0"!==e.charAt(0)||!isNaN(parseInt(e)))&&(n=t,F.test(n)?function(e){const t=e.charCodeAt(0);return t!==e.charCodeAt(e.length-1)||34!==t&&39!==t?e:e.slice(1,-1)}(t):"*"+t);var n}function W(e){const t=[];let n,r,o,s,a,c,l,u=-1,i=0,f=0;const p=[];function m(){const t=e[u+1];if(5===i&&"'"===t||6===i&&'"'===t)return u++,o="\\"+t,p[0](),!0}for(p[0]=()=>{void 0===r?r=o:r+=o},p[1]=()=>{void 0!==r&&(t.push(r),r=void 0)},p[2]=()=>{p[0](),f++},p[3]=()=>{if(f>0)f--,i=4,p[0]();else{if(f=0,void 0===r)return!1;if(r=$(r),!1===r)return!1;p[1]()}};null!==i;)if(u++,n=e[u],"\\"!==n||!m()){if(s=N(n),l=P[i],a=l[s]||l.l||8,8===a)return;if(i=a[0],void 0!==a[1]&&(c=p[a[1]],c&&(o=n,!1===c())))return;if(7===i)return t}}const M=new Map;function E(e,t){if(!O(e))return null;let n=M.get(t);if(n||(n=W(t),n&&M.set(t,n)),!n)return null;const r=n.length;let o=e,s=0;for(;s<r;){const e=o[n[s]];if(void 0===e)return null;o=e,s++}return o}
/*!
  * @intlify/runtime v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */
const A=e=>e,I=e=>"",j=e=>0===e.length?"":e.join(""),D=w;function R(e,t){return e=Math.abs(e),2===t?e?e>1?1:0:1:e?Math.min(e,2):0}function z(e={}){const t=e.locale,n=function(e){const t=c(e.pluralIndex)?e.pluralIndex:-1;return e.named&&(c(e.named.count)||c(e.named.n))?c(e.named.count)?e.named.count:c(e.named.n)?e.named.n:t:t}(e),r=x(e.pluralRules)&&b(t)&&k(e.pluralRules[t])?e.pluralRules[t]:R,o=x(e.pluralRules)&&b(t)&&k(e.pluralRules[t])?R:void 0,s=e.list||[],a=e.named||{};c(e.pluralIndex)&&function(e,t){t.count||(t.count=e),t.n||(t.n=e)}(n,a);function l(t){const n=k(e.messages)?e.messages(t):!!x(e.messages)&&e.messages[t];return n||(e.parent?e.parent.message(t):I)}const u=_(e.processor)&&k(e.processor.normalize)?e.processor.normalize:j,i=_(e.processor)&&k(e.processor.interpolate)?e.processor.interpolate:D,f={list:e=>s[e],named:e=>a[e],plural:e=>e[r(n,e.length,o)],linked:(t,n)=>{const r=l(t)(f);return b(n)?(o=n,e.modifiers?e.modifiers[o]:A)(r):r;var o},message:l,type:_(e.processor)&&b(e.processor.type)?e.processor.type:"text",interpolate:i,normalize:u};return f}
/*!
  * @intlify/message-compiler v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */function J(e,t,n={}){const{domain:r,messages:o,args:s}=n,a=new SyntaxError(String(e));return a.code=e,t&&(a.location=t),a.domain=r,a}function H(e){throw e}function U(e,t,n){const r={start:e,end:t};return null!=n&&(r.source=n),r}const V=String.fromCharCode(8232),G=String.fromCharCode(8233);function K(e){const t=e;let n=0,r=1,o=1,s=0;const a=e=>"\r"===t[e]&&"\n"===t[e+1],c=e=>t[e]===G,l=e=>t[e]===V,u=e=>a(e)||(e=>"\n"===t[e])(e)||c(e)||l(e),i=e=>a(e)||c(e)||l(e)?"\n":t[e];function f(){return s=0,u(n)&&(r++,o=0),a(n)&&n++,n++,o++,t[n]}return{index:()=>n,line:()=>r,column:()=>o,peekOffset:()=>s,charAt:i,currentChar:()=>i(n),currentPeek:()=>i(n+s),next:f,peek:function(){return a(n+s)&&s++,s++,t[n+s]},reset:function(){n=0,r=1,o=1,s=0},resetPeek:function(e=0){s=e},skipToPeek:function(){const e=n+s;for(;e!==n;)f();s=0}}}const B=void 0;function q(e,t={}){const n=!1!==t.location,r=K(e),o=()=>r.index(),s=()=>{return e=r.line(),t=r.column(),n=r.index(),{line:e,column:t,offset:n};var e,t,n},a=s(),c=o(),l={currentType:14,offset:c,startLoc:a,endLoc:a,lastType:14,lastOffset:c,lastStartLoc:a,lastEndLoc:a,braceNest:0,inLinked:!1,text:""},u=()=>l,{onError:i}=t;function f(e,t,n,...r){const o=u();if(t.column+=n,t.offset+=n,i){const n=J(e,U(o.startLoc,t),{domain:"tokenizer",args:r});i(n)}}function p(e,t,r){e.endLoc=s(),e.currentType=t;const o={type:t};return n&&(o.loc=U(e.startLoc,e.endLoc)),null!=r&&(o.value=r),o}const m=e=>p(e,14);function d(e,t){return e.currentChar()===t?(e.next(),t):(f(0,s(),0,t),"")}function h(e){let t="";for(;" "===e.currentPeek()||"\n"===e.currentPeek();)t+=e.currentPeek(),e.peek();return t}function g(e){const t=h(e);return e.skipToPeek(),t}function k(e){if(e===B)return!1;const t=e.charCodeAt(0);return t>=97&&t<=122||t>=65&&t<=90||95===t}function b(e,t){const{currentType:n}=t;if(2!==n)return!1;h(e);const r=function(e){if(e===B)return!1;const t=e.charCodeAt(0);return t>=48&&t<=57}("-"===e.currentPeek()?e.peek():e.currentPeek());return e.resetPeek(),r}function y(e){h(e);const t="|"===e.currentPeek();return e.resetPeek(),t}function x(e,t=!0){const n=(t=!1,r="",o=!1)=>{const s=e.currentPeek();return"{"===s?"%"!==r&&t:"@"!==s&&s?"%"===s?(e.peek(),n(t,"%",!0)):"|"===s?!("%"!==r&&!o)||!(" "===r||"\n"===r):" "===s?(e.peek(),n(!0," ",o)):"\n"!==s||(e.peek(),n(!0,"\n",o)):"%"===r||t},r=n();return t&&e.resetPeek(),r}function L(e,t){const n=e.currentChar();return n===B?B:t(n)?(e.next(),n):null}function T(e){return L(e,(e=>{const t=e.charCodeAt(0);return t>=97&&t<=122||t>=65&&t<=90||t>=48&&t<=57||95===t||36===t}))}function _(e){return L(e,(e=>{const t=e.charCodeAt(0);return t>=48&&t<=57}))}function w(e){return L(e,(e=>{const t=e.charCodeAt(0);return t>=48&&t<=57||t>=65&&t<=70||t>=97&&t<=102}))}function C(e){let t="",n="";for(;t=_(e);)n+=t;return n}function v(e){const t=e.currentChar();switch(t){case"\\":case"'":return e.next(),`\\${t}`;case"u":return S(e,t,4);case"U":return S(e,t,6);default:return f(3,s(),0,t),""}}function S(e,t,n){d(e,t);let r="";for(let o=0;o<n;o++){const n=w(e);if(!n){f(4,s(),0,`\\${t}${r}${e.currentChar()}`);break}r+=n}return`\\${t}${r}`}function O(e){g(e);const t=d(e,"|");return g(e),t}function P(e,t){let n=null;switch(e.currentChar()){case"{":return t.braceNest>=1&&f(8,s(),0),e.next(),n=p(t,2,"{"),g(e),t.braceNest++,n;case"}":return t.braceNest>0&&2===t.currentType&&f(7,s(),0),e.next(),n=p(t,3,"}"),t.braceNest--,t.braceNest>0&&g(e),t.inLinked&&0===t.braceNest&&(t.inLinked=!1),n;case"@":return t.braceNest>0&&f(6,s(),0),n=F(e,t)||m(t),t.braceNest=0,n;default:let r=!0,o=!0,a=!0;if(y(e))return t.braceNest>0&&f(6,s(),0),n=p(t,1,O(e)),t.braceNest=0,t.inLinked=!1,n;if(t.braceNest>0&&(5===t.currentType||6===t.currentType||7===t.currentType))return f(6,s(),0),t.braceNest=0,N(e,t);if(r=function(e,t){const{currentType:n}=t;if(2!==n)return!1;h(e);const r=k(e.currentPeek());return e.resetPeek(),r}(e,t))return n=p(t,5,function(e){g(e);let t="",n="";for(;t=T(e);)n+=t;return e.currentChar()===B&&f(6,s(),0),n}(e)),g(e),n;if(o=b(e,t))return n=p(t,6,function(e){g(e);let t="";return"-"===e.currentChar()?(e.next(),t+=`-${C(e)}`):t+=C(e),e.currentChar()===B&&f(6,s(),0),t}(e)),g(e),n;if(a=function(e,t){const{currentType:n}=t;if(2!==n)return!1;h(e);const r="'"===e.currentPeek();return e.resetPeek(),r}(e,t))return n=p(t,7,function(e){g(e),d(e,"'");let t="",n="";const r=e=>"'"!==e&&"\n"!==e;for(;t=L(e,r);)n+="\\"===t?v(e):t;const o=e.currentChar();return"\n"===o||o===B?(f(2,s(),0),"\n"===o&&(e.next(),d(e,"'")),n):(d(e,"'"),n)}(e)),g(e),n;if(!r&&!o&&!a)return n=p(t,13,function(e){g(e);let t="",n="";const r=e=>"{"!==e&&"}"!==e&&" "!==e&&"\n"!==e;for(;t=L(e,r);)n+=t;return n}(e)),f(1,s(),0,n.value),g(e),n}return n}function F(e,t){const{currentType:n}=t;let r=null;const o=e.currentChar();switch(8!==n&&9!==n&&12!==n&&10!==n||"\n"!==o&&" "!==o||f(9,s(),0),o){case"@":return e.next(),r=p(t,8,"@"),t.inLinked=!0,r;case".":return g(e),e.next(),p(t,9,".");case":":return g(e),e.next(),p(t,10,":");default:return y(e)?(r=p(t,1,O(e)),t.braceNest=0,t.inLinked=!1,r):function(e,t){const{currentType:n}=t;if(8!==n)return!1;h(e);const r="."===e.currentPeek();return e.resetPeek(),r}(e,t)||function(e,t){const{currentType:n}=t;if(8!==n&&12!==n)return!1;h(e);const r=":"===e.currentPeek();return e.resetPeek(),r}(e,t)?(g(e),F(e,t)):function(e,t){const{currentType:n}=t;if(9!==n)return!1;h(e);const r=k(e.currentPeek());return e.resetPeek(),r}(e,t)?(g(e),p(t,12,function(e){let t="",n="";for(;t=T(e);)n+=t;return n}(e))):function(e,t){const{currentType:n}=t;if(10!==n)return!1;const r=()=>{const t=e.currentPeek();return"{"===t?k(e.peek()):!("@"===t||"%"===t||"|"===t||":"===t||"."===t||" "===t||!t)&&("\n"===t?(e.peek(),r()):k(t))},o=r();return e.resetPeek(),o}(e,t)?(g(e),"{"===o?P(e,t)||r:p(t,11,function(e){const t=(n=!1,r)=>{const o=e.currentChar();return"{"!==o&&"%"!==o&&"@"!==o&&"|"!==o&&o?" "===o?r:"\n"===o?(r+=o,e.next(),t(n,r)):(r+=o,e.next(),t(!0,r)):r};return t(!1,"")}(e))):(8===n&&f(9,s(),0),t.braceNest=0,t.inLinked=!1,N(e,t))}}function N(e,t){let n={type:14};if(t.braceNest>0)return P(e,t)||m(t);if(t.inLinked)return F(e,t)||m(t);const r=e.currentChar();switch(r){case"{":return P(e,t)||m(t);case"}":return f(5,s(),0),e.next(),p(t,3,"}");case"@":return F(e,t)||m(t);default:if(y(e))return n=p(t,1,O(e)),t.braceNest=0,t.inLinked=!1,n;if(x(e))return p(t,0,function(e){const t=n=>{const r=e.currentChar();return"{"!==r&&"}"!==r&&"@"!==r&&r?"%"===r?x(e)?(n+=r,e.next(),t(n)):n:"|"===r?n:" "===r||"\n"===r?x(e)?(n+=r,e.next(),t(n)):y(e)?n:(n+=r,e.next(),t(n)):(n+=r,e.next(),t(n)):n};return t("")}(e));if("%"===r)return e.next(),p(t,4,"%")}return n}return{nextToken:function(){const{currentType:e,offset:t,startLoc:n,endLoc:a}=l;return l.lastType=e,l.lastOffset=t,l.lastStartLoc=n,l.lastEndLoc=a,l.offset=o(),l.startLoc=s(),r.currentChar()===B?p(l,14):N(r,l)},currentOffset:o,currentPosition:s,context:u}}const Y=/(?:\\\\|\\'|\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{6}))/g;function Z(e,t,n){switch(e){case"\\\\":return"\\";case"\\'":return"'";default:{const e=parseInt(t||n,16);return e<=55295||e>=57344?String.fromCodePoint(e):"�"}}}function Q(e={}){const t=!1!==e.location,{onError:n}=e;function r(e,t,r,o,...s){const a=e.currentPosition();if(a.offset+=o,a.column+=o,n){const e=J(t,U(r,a),{domain:"parser",args:s});n(e)}}function o(e,n,r){const o={type:e,start:n,end:n};return t&&(o.loc={start:r,end:r}),o}function s(e,n,r,o){e.end=n,o&&(e.type=o),t&&e.loc&&(e.loc.end=r)}function a(e,t){const n=e.context(),r=o(3,n.offset,n.startLoc);return r.value=t,s(r,e.currentOffset(),e.currentPosition()),r}function c(e,t){const n=e.context(),{lastOffset:r,lastStartLoc:a}=n,c=o(5,r,a);return c.index=parseInt(t,10),e.nextToken(),s(c,e.currentOffset(),e.currentPosition()),c}function l(e,t){const n=e.context(),{lastOffset:r,lastStartLoc:a}=n,c=o(4,r,a);return c.key=t,e.nextToken(),s(c,e.currentOffset(),e.currentPosition()),c}function u(e,t){const n=e.context(),{lastOffset:r,lastStartLoc:a}=n,c=o(9,r,a);return c.value=t.replace(Y,Z),e.nextToken(),s(c,e.currentOffset(),e.currentPosition()),c}function i(e){const t=e.context(),n=o(6,t.offset,t.startLoc);let a=e.nextToken();if(9===a.type){const t=function(e){const t=e.nextToken(),n=e.context(),{lastOffset:a,lastStartLoc:c}=n,l=o(8,a,c);return 12!==t.type?(r(e,11,n.lastStartLoc,0),l.value="",s(l,a,c),{nextConsumeToken:t,node:l}):(null==t.value&&r(e,13,n.lastStartLoc,0,X(t)),l.value=t.value||"",s(l,e.currentOffset(),e.currentPosition()),{node:l})}(e);n.modifier=t.node,a=t.nextConsumeToken||e.nextToken()}switch(10!==a.type&&r(e,13,t.lastStartLoc,0,X(a)),a=e.nextToken(),2===a.type&&(a=e.nextToken()),a.type){case 11:null==a.value&&r(e,13,t.lastStartLoc,0,X(a)),n.key=function(e,t){const n=e.context(),r=o(7,n.offset,n.startLoc);return r.value=t,s(r,e.currentOffset(),e.currentPosition()),r}(e,a.value||"");break;case 5:null==a.value&&r(e,13,t.lastStartLoc,0,X(a)),n.key=l(e,a.value||"");break;case 6:null==a.value&&r(e,13,t.lastStartLoc,0,X(a)),n.key=c(e,a.value||"");break;case 7:null==a.value&&r(e,13,t.lastStartLoc,0,X(a)),n.key=u(e,a.value||"");break;default:r(e,12,t.lastStartLoc,0);const i=e.context(),f=o(7,i.offset,i.startLoc);return f.value="",s(f,i.offset,i.startLoc),n.key=f,s(n,i.offset,i.startLoc),{nextConsumeToken:a,node:n}}return s(n,e.currentOffset(),e.currentPosition()),{node:n}}function f(e){const t=e.context(),n=o(2,1===t.currentType?e.currentOffset():t.offset,1===t.currentType?t.endLoc:t.startLoc);n.items=[];let f=null;do{const o=f||e.nextToken();switch(f=null,o.type){case 0:null==o.value&&r(e,13,t.lastStartLoc,0,X(o)),n.items.push(a(e,o.value||""));break;case 6:null==o.value&&r(e,13,t.lastStartLoc,0,X(o)),n.items.push(c(e,o.value||""));break;case 5:null==o.value&&r(e,13,t.lastStartLoc,0,X(o)),n.items.push(l(e,o.value||""));break;case 7:null==o.value&&r(e,13,t.lastStartLoc,0,X(o)),n.items.push(u(e,o.value||""));break;case 8:const s=i(e);n.items.push(s.node),f=s.nextConsumeToken||null}}while(14!==t.currentType&&1!==t.currentType);return s(n,1===t.currentType?t.lastOffset:e.currentOffset(),1===t.currentType?t.lastEndLoc:e.currentPosition()),n}function m(e){const t=e.context(),{offset:n,startLoc:a}=t,c=f(e);return 14===t.currentType?c:function(e,t,n,a){const c=e.context();let l=0===a.items.length;const u=o(1,t,n);u.cases=[],u.cases.push(a);do{const t=f(e);l||(l=0===t.items.length),u.cases.push(t)}while(14!==c.currentType);return l&&r(e,10,n,0),s(u,e.currentOffset(),e.currentPosition()),u}(e,n,a,c)}return{parse:function(n){const a=q(n,p({},e)),c=a.context(),l=o(0,c.offset,c.startLoc);return t&&l.loc&&(l.loc.source=n),l.body=m(a),14!==c.currentType&&r(a,13,c.lastStartLoc,0,n[c.offset]||""),s(l,a.currentOffset(),a.currentPosition()),l}}}function X(e){if(14===e.type)return"EOF";const t=(e.value||"").replace(/\r?\n/gu,"\\n");return t.length>10?t.slice(0,9)+"…":t}function ee(e,t){for(let n=0;n<e.length;n++)te(e[n],t)}function te(e,t){switch(e.type){case 1:ee(e.cases,t),t.helper("plural");break;case 2:ee(e.items,t);break;case 6:te(e.key,t),t.helper("linked");break;case 5:t.helper("interpolate"),t.helper("list");break;case 4:t.helper("interpolate"),t.helper("named")}}function ne(e,t={}){const n=function(e,t={}){const n={ast:e,helpers:new Set};return{context:()=>n,helper:e=>(n.helpers.add(e),e)}}(e);n.helper("normalize"),e.body&&te(e.body,n);const r=n.context();e.helpers=Array.from(r.helpers)}function re(e,t){const{helper:n}=e;switch(t.type){case 0:!function(e,t){t.body?re(e,t.body):e.push("null")}(e,t);break;case 1:!function(e,t){const{helper:n,needIndent:r}=e;if(t.cases.length>1){e.push(`${n("plural")}([`),e.indent(r());const o=t.cases.length;for(let n=0;n<o&&(re(e,t.cases[n]),n!==o-1);n++)e.push(", ");e.deindent(r()),e.push("])")}}(e,t);break;case 2:!function(e,t){const{helper:n,needIndent:r}=e;e.push(`${n("normalize")}([`),e.indent(r());const o=t.items.length;for(let s=0;s<o&&(re(e,t.items[s]),s!==o-1);s++)e.push(", ");e.deindent(r()),e.push("])")}(e,t);break;case 6:!function(e,t){const{helper:n}=e;e.push(`${n("linked")}(`),re(e,t.key),t.modifier&&(e.push(", "),re(e,t.modifier)),e.push(")")}(e,t);break;case 8:case 7:e.push(JSON.stringify(t.value),t);break;case 5:e.push(`${n("interpolate")}(${n("list")}(${t.index}))`,t);break;case 4:e.push(`${n("interpolate")}(${n("named")}(${JSON.stringify(t.key)}))`,t);break;case 9:case 3:e.push(JSON.stringify(t.value),t)}}function oe(e,t={}){const n=p({},t),r=Q(n).parse(e);return ne(r,n),((e,t={})=>{const n=b(t.mode)?t.mode:"normal",r=b(t.filename)?t.filename:"message.intl",o=!!t.sourceMap,s=null!=t.breakLineCode?t.breakLineCode:"arrow"===n?";":"\n",a=t.needIndent?t.needIndent:"arrow"!==n,c=e.helpers||[],l=function(e,t){const{sourceMap:n,filename:r,breakLineCode:o,needIndent:s}=t,a={source:e.loc.source,filename:r,code:"",column:1,line:1,offset:0,map:void 0,breakLineCode:o,needIndent:s,indentLevel:0};function c(e,t){a.code+=e}function l(e,t=!0){const n=t?o:"";c(s?n+"  ".repeat(e):n)}return{context:()=>a,push:c,indent:function(e=!0){const t=++a.indentLevel;e&&l(t)},deindent:function(e=!0){const t=--a.indentLevel;e&&l(t)},newline:function(){l(a.indentLevel)},helper:e=>`_${e}`,needIndent:()=>a.needIndent}}(e,{mode:n,filename:r,sourceMap:o,breakLineCode:s,needIndent:a});l.push("normal"===n?"function __msg__ (ctx) {":"(ctx) => {"),l.indent(a),c.length>0&&(l.push(`const { ${c.map((e=>`${e}: _${e}`)).join(", ")} } = ctx`),l.newline()),l.push("return "),re(l,e),l.deindent(a),l.push("}");const{code:u,map:i}=l.context();return{ast:e,code:u,map:i?i.toJSON():void 0}})(r,n)}
/*!
  * @intlify/devtools-if v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */const se="i18n:init";
/*!
  * @intlify/core-base v9.1.6
  * (c) 2021 kazuya kawaguchi
  * Released under the MIT License.
  */let ae=null;const ce=le("function:translate");function le(e){return t=>ae&&ae.emit(e,t)}const ue={0:"Not found '{key}' key in '{locale}' locale messages.",1:"Fall back to translate '{key}' key with '{target}' locale.",2:"Cannot format a number value due to not supported Intl.NumberFormat.",3:"Fall back to number format '{key}' key with '{target}' locale.",4:"Cannot format a date value due to not supported Intl.DateTimeFormat.",5:"Fall back to datetime format '{key}' key with '{target}' locale."};let ie;let fe=null;let pe=0;function me(e,t,n,r,o){const{missing:s,onWarn:a}=e;if(null!==s){const r=s(e,n,t,o);return b(r)?r:t}return t}function de(e,t,n){const r=e;r.__localeChainCache||(r.__localeChainCache=new Map);let o=r.__localeChainCache.get(n);if(!o){o=[];let e=[n];for(;g(e);)e=he(o,e,t);const s=g(t)?t:_(t)?t.default?t.default:null:t;e=b(s)?[s]:s,g(e)&&he(o,e,!1),r.__localeChainCache.set(n,o)}return o}function he(e,t,n){let r=!0;for(let o=0;o<t.length&&y(r);o++){const s=t[o];b(s)&&(r=ge(e,t[o],n))}return r}function ge(e,t,n){let r;const o=t.split("-");do{r=ke(e,o.join("-"),n),o.splice(-1,1)}while(o.length&&!0===r);return r}function ke(e,t,n){let r=!1;if(!e.includes(t)&&(r=!0,t)){r="!"!==t[t.length-1];const o=t.replace(/!/g,"");e.push(o),(g(n)||_(n))&&n[o]&&(r=n[o])}return r}const be=e=>e;let ye=Object.create(null);function xe(e){return J(e,null,void 0)}const Le=()=>"",Te=e=>k(e);function _e(e,t,n,r,o,a){const{messageCompiler:c,warnHtmlMessage:l}=e;if(Te(r)){const e=r;return e.locale=e.locale||n,e.key=e.key||t,e}const u=c(r,function(e,t,n,r,o,a){return{warnHtmlMessage:o,onError:e=>{throw a&&a(e),e},onCacheKey:e=>s(t,n,e)}}(0,n,o,0,l,a));return u.locale=n,u.key=t,u.source=r,u}function we(...e){const[t,n,r]=e,o={};if(!b(t)&&!c(t)&&!Te(t))throw xe(14);const s=c(t)?String(t):(Te(t),t);return c(n)?o.plural=n:b(n)?o.default=n:_(n)&&!i(n)?o.named=n:g(n)&&(o.list=n),c(r)?o.plural=r:b(r)?o.default=r:_(r)&&p(o,r),[s,o]}function Ce(...e){const[t,n,r,o]=e;let s,a={},u={};if(b(t)){if(!/\d{4}-\d{2}-\d{2}(T.*)?/.test(t))throw xe(16);s=new Date(t);try{s.toISOString()}catch(i){throw xe(16)}}else if(l(t)){if(isNaN(t.getTime()))throw xe(15);s=t}else{if(!c(t))throw xe(14);s=t}return b(n)?a.key=n:_(n)&&(a=n),b(r)?a.locale=r:_(r)&&(u=r),_(o)&&(u=o),[a.key||"",s,a,u]}function ve(...e){const[t,n,r,o]=e;let s={},a={};if(!c(t))throw xe(14);const l=t;return b(n)?s.key=n:_(n)&&(s=n),b(r)?s.locale=r:_(r)&&(a=r),_(o)&&(a=o),[s.key||"",l,s,a]}var Se=e(Object.freeze({__proto__:null,[Symbol.toStringTag]:"Module",MISSING_RESOLVE_VALUE:"",NOT_REOSLVED:-1,VERSION:"9.1.6",clearCompileCache:function(){ye=Object.create(null)},clearDateTimeFormat:function(e,t,n){const r=e;for(const o in n){const e=`${t}__${o}`;r.__datetimeFormatters.has(e)&&r.__datetimeFormatters.delete(e)}},clearNumberFormat:function(e,t,n){const r=e;for(const o in n){const e=`${t}__${o}`;r.__numberFormatters.has(e)&&r.__numberFormatters.delete(e)}},compileToFunction:function(e,t={}){{const n=(t.onCacheKey||be)(e),r=ye[n];if(r)return r;let o=!1;const s=t.onError||H;t.onError=e=>{o=!0,s(e)};const{code:a}=oe(e,t),c=new Function(`return ${a}`)();return o?c:ye[n]=c}},createCoreContext:function(e={}){const t=b(e.version)?e.version:"9.1.6",n=b(e.locale)?e.locale:"en-US",r=g(e.fallbackLocale)||_(e.fallbackLocale)||b(e.fallbackLocale)||!1===e.fallbackLocale?e.fallbackLocale:n,o=_(e.messages)?e.messages:{[n]:{}},s=_(e.datetimeFormats)?e.datetimeFormats:{[n]:{}},a=_(e.numberFormats)?e.numberFormats:{[n]:{}},c=p({},e.modifiers||{},{upper:e=>b(e)?e.toUpperCase():e,lower:e=>b(e)?e.toLowerCase():e,capitalize:e=>b(e)?`${e.charAt(0).toLocaleUpperCase()}${e.substr(1)}`:e}),l=e.pluralRules||{},i=k(e.missing)?e.missing:null,m=!y(e.missingWarn)&&!u(e.missingWarn)||e.missingWarn,d=!y(e.fallbackWarn)&&!u(e.fallbackWarn)||e.fallbackWarn,h=!!e.fallbackFormat,L=!!e.unresolving,T=k(e.postTranslation)?e.postTranslation:null,w=_(e.processor)?e.processor:null,C=!y(e.warnHtmlMessage)||e.warnHtmlMessage,v=!!e.escapeParameter,S=k(e.messageCompiler)?e.messageCompiler:ie,O=k(e.onWarn)?e.onWarn:f,P=e,F=x(P.__datetimeFormatters)?P.__datetimeFormatters:new Map,N=x(P.__numberFormatters)?P.__numberFormatters:new Map,$=x(P.__meta)?P.__meta:{};return pe++,{version:t,cid:pe,locale:n,fallbackLocale:r,messages:o,datetimeFormats:s,numberFormats:a,modifiers:c,pluralRules:l,missing:i,missingWarn:m,fallbackWarn:d,fallbackFormat:h,unresolving:L,postTranslation:T,processor:w,warnHtmlMessage:C,escapeParameter:v,messageCompiler:S,onWarn:O,__datetimeFormatters:F,__numberFormatters:N,__meta:$}},createCoreError:xe,datetime:function(e,...t){const{datetimeFormats:n,unresolving:r,fallbackLocale:o,onWarn:s}=e,{__datetimeFormatters:a}=e,[c,l,u,f]=Ce(...t);y(u.missingWarn)?u.missingWarn:e.missingWarn,y(u.fallbackWarn)?u.fallbackWarn:e.fallbackWarn;const m=!!u.part,d=b(u.locale)?u.locale:e.locale,h=de(e,o,d);if(!b(c)||""===c)return new Intl.DateTimeFormat(d).format(l);let g,k={},x=null;for(let i=0;i<h.length&&(g=h[i],k=n[g]||{},x=k[c],!_(x));i++)me(e,c,g,0,"datetime format");if(!_(x)||!b(g))return r?-1:c;let L=`${g}__${c}`;i(f)||(L=`${L}__${JSON.stringify(f)}`);let T=a.get(L);return T||(T=new Intl.DateTimeFormat(g,p({},x,f)),a.set(L,T)),m?T.formatToParts(l):T.format(l)},getAdditionalMeta:()=>fe,getDevToolsHook:function(){return ae},getLocaleChain:de,getWarnMessage:function(e,...t){return r(ue[e],...t)},handleMissing:me,initI18nDevTools:function(e,t,n){ae&&ae.emit(se,{timestamp:Date.now(),i18n:e,version:t,meta:n})},isMessageFunction:Te,isTranslateFallbackWarn:function(e,t){return e instanceof RegExp?e.test(t):e},isTranslateMissingWarn:function(e,t){return e instanceof RegExp?e.test(t):e},number:function(e,...t){const{numberFormats:n,unresolving:r,fallbackLocale:o,onWarn:s}=e,{__numberFormatters:a}=e,[c,l,u,f]=ve(...t);y(u.missingWarn)?u.missingWarn:e.missingWarn,y(u.fallbackWarn)?u.fallbackWarn:e.fallbackWarn;const m=!!u.part,d=b(u.locale)?u.locale:e.locale,h=de(e,o,d);if(!b(c)||""===c)return new Intl.NumberFormat(d).format(l);let g,k={},x=null;for(let i=0;i<h.length&&(g=h[i],k=n[g]||{},x=k[c],!_(x));i++)me(e,c,g,0,"number format");if(!_(x)||!b(g))return r?-1:c;let L=`${g}__${c}`;i(f)||(L=`${L}__${JSON.stringify(f)}`);let T=a.get(L);return T||(T=new Intl.NumberFormat(g,p({},x,f)),a.set(L,T)),m?T.formatToParts(l):T.format(l)},parseDateTimeArgs:Ce,parseNumberArgs:ve,parseTranslateArgs:we,registerMessageCompiler:function(e){ie=e},setAdditionalMeta:e=>{fe=e},setDevToolsHook:function(e){ae=e},translate:function(e,...t){const{fallbackFormat:n,postTranslation:r,unresolving:o,fallbackLocale:s,messages:a}=e,[l,u]=we(...t),i=(y(u.missingWarn)?u.missingWarn:e.missingWarn,y(u.fallbackWarn)?u.fallbackWarn:e.fallbackWarn,y(u.escapeParameter)?u.escapeParameter:e.escapeParameter),f=!!u.resolvedMessage,p=b(u.default)||y(u.default)?y(u.default)?l:u.default:n?l:"",m=n||""!==p,h=b(u.locale)?u.locale:e.locale;i&&function(e){g(e.list)?e.list=e.list.map((e=>b(e)?d(e):e)):x(e.named)&&Object.keys(e.named).forEach((t=>{b(e.named[t])&&(e.named[t]=d(e.named[t]))}))}(u);let[L,T,_]=f?[l,h,a[h]||{}]:function(e,t,n,r,o,s){const{messages:a,onWarn:c}=e,l=de(e,r,n);let u,i={},f=null;const p="translate";for(let m=0;m<l.length&&(u=l[m],i=a[u]||{},null===(f=E(i,t))&&(f=i[t]),!b(f)&&!k(f));m++){const n=me(e,t,u,0,p);n!==t&&(f=n)}return[f,u,i]}(e,l,h,s),w=l;if(f||b(L)||Te(L)||m&&(L=p,w=L),!(f||(b(L)||Te(L))&&b(T)))return o?-1:l;let C=!1;const v=Te(L)?L:_e(e,l,T,L,w,(()=>{C=!0}));if(C)return L;const S=function(e,t,n){return t(n)}(0,v,z(function(e,t,n,r){const{modifiers:o,pluralRules:s}=e,a={locale:t,modifiers:o,pluralRules:s,messages:r=>{const o=E(n,r);if(b(o)){let n=!1;const s=_e(e,r,t,o,r,(()=>{n=!0}));return n?Le:s}return Te(o)?o:Le}};e.processor&&(a.processor=e.processor);r.list&&(a.list=r.list);r.named&&(a.named=r.named);c(r.plural)&&(a.pluralIndex=r.plural);return a}(e,T,_,u)));return r?r(S):S},translateDevTools:ce,updateFallbackLocale:function(e,t,n){e.__localeChainCache=new Map,de(e,n,t)},createCompileError:J,handleFlatJson:function e(t){if(!O(t))return t;for(const n in t)if(S(t,n))if(n.includes(".")){const r=n.split("."),o=r.length-1;let s=t;for(let e=0;e<o;e++)r[e]in s||(s[r[e]]={}),s=s[r[e]];s[r[o]]=t[n],delete t[n],O(s[r[o]])&&e(s[r[o]])}else O(t[n])&&e(t[n]);return t},parse:W,resolveValue:E,DEFAULT_MESSAGE_DATA_TYPE:"text",createMessageContext:z})),Oe=e(C);export{Oe as a,b as i,Se as r};