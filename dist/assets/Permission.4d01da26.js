import{a1 as a,$ as l,a4 as s,a5 as e,m as n,t,a6 as r,a7 as d,Q as i}from"./@vue.160ddf67.js";import"./vue-i18n.3f148863.js";import"./@intlify.b71b68c2.js";import"./vue.21b55118.js";const u={name:"permission"},o=a=>(r("data-v-4dc4a8da"),a=a(),d(),a),c={class:"crumbs"},m=o((()=>e("i",{class:"el-icon-lx-warn"},null,-1))),p=i(" 权限测试 "),f={class:"container"},b=o((()=>e("h1",null,"管理员权限页面",-1))),v=o((()=>e("p",null,"只有用 admin 账号登录的才拥有管理员权限，才能进到这个页面，其他账号想进来都会跳到403页面，重新用管理员账号登录才有权限。",-1))),_=i(" 想尝试一下，请 "),j=i("退出登录"),g=i("，随便输入个账号名，再进来试试看。 ");u.render=function(r,d,i,u,o,x){const h=a("el-breadcrumb-item"),k=a("el-breadcrumb"),w=a("router-link");return l(),s("div",null,[e("div",c,[n(k,{separator:"/"},{default:t((()=>[n(h,null,{default:t((()=>[m,p])),_:1})])),_:1})]),e("div",f,[b,v,e("p",null,[_,n(w,{to:"/login",class:"logout"},{default:t((()=>[j])),_:1}),g])])])},u.__scopeId="data-v-4dc4a8da";export default u;
