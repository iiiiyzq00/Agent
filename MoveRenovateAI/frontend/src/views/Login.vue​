<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🏠 MoveRenovateAI</h1>
      <p>登录以开始使用</p>
      <a-form :model="form" layout="vertical" @submit="handleLogin">
        <a-form-item label="用户名/邮箱"><a-input v-model="form.username" placeholder="请输入用户名或邮箱" /></a-form-item>
        <a-form-item label="密码"><a-input-password v-model="form.password" placeholder="请输入密码" /></a-form-item>
        <a-form-item><a-button type="primary" html-type="submit" :loading="loading" long>登录</a-button></a-form-item>
      </a-form>
      <div class="links"><a href="#">忘记密码</a><a href="#">注册账号</a></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import request from '../api/index'

const router = useRouter(); const loading = ref(false)
const form = ref({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) { Message.warning('请填写用户名和密码'); return }
  loading.value = true
  try {
    const response: any = await request.post('/api/v1/auth/login', form.value)
    localStorage.setItem('access_token', response.access_token)
    Message.success('登录成功'); router.push('/home')
  } catch (error) { Message.error('登录失败，请检查用户名和密码') }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.login-card { width: 400px; padding: 40px; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.login-card h1 { text-align: center; font-size: 28px; margin-bottom: 8px; }
.login-card p { text-align: center; color: #86909c; margin-bottom: 32px; }
.links { display: flex; justify-content: space-between; margin-top: 16px; }
.links a { color: #165dff; text-decoration: none; }
</style>
