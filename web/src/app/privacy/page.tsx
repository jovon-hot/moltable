'use client'

import { useLang } from '@/contexts/LanguageContext'

export default function PrivacyPage() {
  const { lang } = useLang()

  return (
    <div className="min-h-screen px-6 py-24 max-w-3xl mx-auto" style={{ background: '#0D0D14', color: '#ffffff' }}>
      <h1 className="text-2xl mb-8" style={{ fontWeight: 590 }}>
        {lang === 'zh' ? '隐私政策' : 'Privacy Policy'}
      </h1>

      <div className="space-y-6 text-sm leading-relaxed" style={{ color: '#cccccc' }}>
        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '1. 数据收集' : '1. Data Collection'}
          </h2>
          <p>{lang === 'zh'
            ? '我们仅收集提供服务所必需的最少数据：您的邮箱地址、您主动创建的 Persona 名称、记忆内容和 API Key 哈希。我们不会收集您的浏览历史、位置信息或设备指纹。'
            : 'We collect only the minimum data necessary to provide the service: your email address, Persona names you create, memory content, and API key hashes. We do not collect browsing history, location data, or device fingerprints.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '2. 数据存储与加密' : '2. Data Storage & Encryption'}
          </h2>
          <p>{lang === 'zh'
            ? '所有数据存储在 Supabase（AWS 新加坡区域），传输中采用 TLS 1.3 加密。API Key 使用 PBKDF2-SHA256 哈希存储，密码使用 scrypt 哈希。向量嵌入数据存储于 pgvector。'
            : 'All data is stored on Supabase (AWS Singapore region) with TLS 1.3 encryption in transit. API keys are stored as PBKDF2-SHA256 hashes. Passwords use scrypt hashing. Vector embeddings are stored in pgvector.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '3. 数据共享' : '3. Data Sharing'}
          </h2>
          <p>{lang === 'zh'
            ? '我们不会出售、出租或与第三方共享您的个人数据。您的数据仅用于为您提供 Moltable 服务。'
            : 'We do not sell, rent, or share your personal data with third parties. Your data is used solely to provide the Moltable service to you.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '4. 您的权利' : '4. Your Rights'}
          </h2>
          <p>{lang === 'zh'
            ? '您可以随时导出或永久删除您的所有数据。删除操作不可逆。请联系 hi@moltable.ai 行使您的权利。'
            : 'You can export or permanently delete all your data at any time. Deletion is irreversible. Contact hi@moltable.ai to exercise your rights.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '5. AI 训练' : '5. AI Training'}
          </h2>
          <p>{lang === 'zh'
            ? '我们永远不会使用您的个人数据、记忆或 Persona 内容来训练 AI 模型。您的数据属于您。'
            : 'We will never use your personal data, memories, or Persona content to train AI models. Your data belongs to you.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '6. 联系我们' : '6. Contact Us'}
          </h2>
          <p>{lang === 'zh'
            ? '如有隐私相关问题，请联系：hi@moltable.ai。数据控制方：BLOX Company Limited，注册地址：香港土瓜灣土瓜灣道94號美華工業中心B座5樓11室，公司注册编号：77235569。最后更新：2026-08-01。'
            : 'For privacy-related inquiries, contact: hi@moltable.ai. Data controller: BLOX Company Limited, registered at Room 11, 5/F, Block B, Mai Wah Industrial Building, 94 To Kwa Wan Road, To Kwa Wan, Hong Kong. Company Registration Number: 77235569. Last updated: 2026-08-01.'
          }</p>
        </section>
      </div>
    </div>
  )
}
