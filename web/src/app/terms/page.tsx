'use client'

import { useLang } from '@/contexts/LanguageContext'

export default function TermsPage() {
  const { lang } = useLang()

  return (
    <div className="min-h-screen px-6 py-24 max-w-3xl mx-auto" style={{ background: '#0D0D14', color: '#ffffff' }}>
      <h1 className="text-2xl mb-8" style={{ fontWeight: 590 }}>
        {lang === 'zh' ? '服务条款' : 'Terms of Service'}
      </h1>

      <div className="space-y-6 text-sm leading-relaxed" style={{ color: '#cccccc' }}>
        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '1. 服务描述' : '1. Service Description'}
          </h2>
          <p>{lang === 'zh'
            ? 'Moltable 是一个 Agent 在线同步层：一个账号，你调教 AI 的身份、记忆、Persona 和项目跨设备、跨 Agent 在线同步；并提供文件级备份（快照、版本管理、回滚）与跨框架迁移功能。'
            : 'Moltable is an Agent online sync layer: one account that syncs your tuned AI identity, memories, personas, and projects across devices and agents, with file-level backup (snapshots, versioning, rollback) and cross-framework migration.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '2. 账户责任' : '2. Account Responsibility'}
          </h2>
          <p>{lang === 'zh'
            ? '您有责任保护您的账户凭据和 API Key。API Key 仅在创建时显示一次。请勿与他人共享您的 API Key。'
            : 'You are responsible for safeguarding your account credentials and API keys. API keys are shown only once upon creation. Do not share your API key with others.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '3. 使用限制' : '3. Usage Limits'}
          </h2>
          <p>{lang === 'zh'
            ? '各套餐有明确的使用配额（Free: 1 Agent + 2 Persona + 100 记忆，Pro: 5 Agent + 10 Persona + 1万记忆 + 1GB 备份存储，Ultra: 无限 Agent + 无限 Persona + 5万记忆 + 10GB 备份存储）。超出配额可能导致服务降级。禁止滥用 API、反向工程或非法用途。'
            : 'Each plan has defined usage quotas (Free: 1 agent + 2 personas + 100 memories, Pro: 5 agents + 10 personas + 10K memories + 1GB backup storage, Ultra: unlimited agents + unlimited personas + 50K memories + 10GB backup storage). Exceeding quotas may result in service degradation. API abuse, reverse engineering, or illegal use is prohibited.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '4. 退款政策' : '4. Refund Policy'}
          </h2>
          <p>{lang === 'zh'
            ? 'Pro 和 Ultra 套餐支持 7 天无理由退款。退款申请请发送至 hi@moltable.ai。'
            : 'Pro and Ultra plans come with a 7-day no-questions-asked refund policy. Send refund requests to hi@moltable.ai.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '5. 知识产权' : '5. Intellectual Property'}
          </h2>
          <p>{lang === 'zh'
            ? '您保留您创建的所有数据（同步资产、备份快照）的完全所有权。Moltable 平台代码以 MIT 协议开源。'
            : 'You retain full ownership of all data you create (synced assets, backup snapshots). The Moltable platform code is open source under the MIT license.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '6. 免责声明' : '6. Disclaimer'}
          </h2>
          <p>{lang === 'zh'
            ? 'Moltable 按"现状"提供服务，不提供任何明示或暗示的保证。我们不对因使用服务而产生的任何间接损失承担责任。最后更新：2026-08-01。'
            : 'Moltable is provided "as is" without warranties of any kind. We are not liable for any indirect damages arising from use of the service. Last updated: 2026-08-01.'
          }</p>
        </section>

        <section>
          <h2 className="text-base mb-3" style={{ color: '#ffffff', fontWeight: 590 }}>
            {lang === 'zh' ? '7. 服务提供方' : '7. Service Provider'}
          </h2>
          <p>{lang === 'zh'
            ? '本服务由 BLOX Company Limited 提供，注册地址：香港土瓜灣土瓜灣道94號美華工業中心B座5樓11室，公司注册编号：77235569。'
            : 'This service is provided by BLOX Company Limited, registered at Room 11, 5/F, Block B, Mai Wah Industrial Building, 94 To Kwa Wan Road, To Kwa Wan, Hong Kong. Company Registration Number: 77235569.'
          }</p>
        </section>
      </div>
    </div>
  )
}
