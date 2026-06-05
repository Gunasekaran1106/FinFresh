import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, ArrowRight, Loader2, Wallet } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { validateEmail, validatePassword, validateName } from '../utils/validators';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    const newErrors = {};
    if (!isLogin) {
      const nameErr = validateName(formData.name);
      if (nameErr) newErrors.name = nameErr;
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!isLogin) {
      const passErr = validatePassword(formData.password);
      if (passErr) newErrors.password = passErr;
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    
    setLoading(true);
    setErrors({});
    
    try {
      if (isLogin) {
        const { data } = await authAPI.login({ email: formData.email, password: formData.password });
        login(data.user, data.token); // API returns { user, token: { access_token, ... } }
        navigate('/dashboard');
      } else {
        await authAPI.register(formData);
        setIsLogin(true);
        setFormData({ name: '', email: '', password: '' });
        // Optionally auto-login, but for now just switch to login view
      }
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Authentication failed. Please try again.';
      setErrors({ form: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 text-primary mb-4 ring-1 ring-primary/50 shadow-[0_0_15px_rgba(14,165,233,0.5)]">
            <Wallet className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">FinFresh</h1>
          <p className="text-muted-foreground">
            {isLogin ? 'Welcome back! Please login to your account.' : 'Create your account and start tracking today.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-6">
          {errors.form && (
            <div className="bg-destructive/10 text-destructive border border-destructive/20 p-3 rounded-lg text-sm text-center">
              {errors.form}
            </div>
          )}

          {!isLogin && (
            <div className="space-y-1 relative">
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Full Name"
                  className="w-full glass-input rounded-xl py-3 pl-10 pr-4 outline-none"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  disabled={loading}
                />
              </div>
              {errors.name && <p className="text-destructive text-xs pl-1">{errors.name}</p>}
            </div>
          )}

          <div className="space-y-1 relative">
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                placeholder="Email Address"
                className="w-full glass-input rounded-xl py-3 pl-10 pr-4 outline-none"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={loading}
              />
            </div>
            {errors.email && <p className="text-destructive text-xs pl-1">{errors.email}</p>}
          </div>

          <div className="space-y-1 relative">
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                placeholder="Password"
                className="w-full glass-input rounded-xl py-3 pl-10 pr-4 outline-none"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                disabled={loading}
              />
            </div>
            {errors.password && <p className="text-destructive text-xs pl-1">{errors.password}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-primary-foreground premium-btn rounded-xl py-3 px-4 flex items-center justify-center font-semibold hover:bg-primary/90 shadow-[0_0_15px_rgba(14,165,233,0.3)]"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Please wait...
              </>
            ) : (
              <>
                {isLogin ? 'Login' : 'Register'}
                <ArrowRight className="w-5 h-5 ml-2" />
              </>
            )}
          </button>

          <div className="text-center pt-4 border-t border-white/10">
            <p className="text-sm text-muted-foreground">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setErrors({});
                  setFormData({ name: '', email: '', password: '' });
                }}
                className="text-primary hover:underline font-medium focus:outline-none"
              >
                {isLogin ? 'Register' : 'Login'}
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Auth;
