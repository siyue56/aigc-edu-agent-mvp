import { useState } from 'react'
function App() {
  const [chat, setChat] = useState('')
  return (<div><h1>高校学习智能体 AIGC (MVP)</h1><textarea value={chat} onChange={e => setChat(e.target.value)}></textarea><button onClick={() => alert('Sending...')}>发送</button></div>)
}
export default App
