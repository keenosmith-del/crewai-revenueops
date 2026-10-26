import { createContext, useContext, useEffect, useState } from 'react'
import { api, post } from '../services/api'
const AuthContext = createContext(null)
export function AuthProvider({children}) {
  const [user,setUser]=useState(null), [loading,setLoading]=useState(true)
  useEffect(()=>{api('/auth/me').then(setUser).catch(()=>{}).finally(()=>setLoading(false))},[])
  async function login(email,password){await post('/auth/login',{email,password});setUser(await api('/auth/me'))}
  async function logout(){await post('/auth/logout');setUser(null)}
  return <AuthContext.Provider value={{user,loading,login,logout}}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
