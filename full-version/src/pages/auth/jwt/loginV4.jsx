import { useState } from 'react';

// material-ui
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Link from '@mui/material/Link';
import { styled } from '@mui/material/styles';

// icons
import EyeOutlined from '@ant-design/icons/EyeOutlined';
import EyeInvisibleOutlined from '@ant-design/icons/EyeInvisibleOutlined';

// ================================|| STYLED COMPONENTS ||================================ //

const Container = styled(Box)({
  display: 'flex',
  height: '100vh',
  width: '100vw',
  overflow: 'hidden'
});

const LeftPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%)',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '60px',
  color: '#fff',
  position: 'relative',
  [theme.breakpoints.down('md')]: {
    display: 'none'
  }
}));

const RightPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  background: '#ffffff',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '40px',
  overflowY: 'auto',
  [theme.breakpoints.down('md')]: {
    flex: 'none',
    width: '100%'
  },
  [theme.breakpoints.down('sm')]: {
    padding: '30px 20px'
  }
}));

const LoginContainer = styled(Box)({
  width: '100%',
  maxWidth: '440px'
});

const StyledTextField = styled(TextField)({
  '& .MuiOutlinedInput-root': {
    borderRadius: '8px',
    transition: 'all 0.3s ease',
    '&:hover': {
      boxShadow: '0 0 0 2px rgba(30, 60, 114, 0.08)'
    },
    '&.Mui-focused': {
      boxShadow: '0 0 0 3px rgba(30, 60, 114, 0.12)'
    }
  }
});

const GradientButton = styled(Button)({
  padding: '13px',
  fontSize: '15px',
  fontWeight: 600,
  textTransform: 'none',
  borderRadius: '8px',
  background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
  color: '#fff',
  boxShadow: '0 4px 14px rgba(30, 60, 114, 0.4)',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'linear-gradient(135deg, #2a5298 0%, #1e3c72 100%)',
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 20px rgba(30, 60, 114, 0.5)'
  }
});

const SocialButton = styled(Button)({
  flex: 1,
  padding: '11px',
  background: '#ffffff',
  color: '#5E5E5E',
  border: '1px solid #E0E0E0',
  borderRadius: '8px',
  fontSize: '13px',
  fontWeight: 500,
  textTransform: 'none',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: '#F8F9FA',
    borderColor: '#1e3c72',
    transform: 'translateY(-1px)',
    boxShadow: '0 3px 10px rgba(30, 60, 114, 0.12)'
  }
});

// ================================|| JWT - LOGIN V4 ||================================ //

export default function LoginV4() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Login attempt (UI only):', { email, password: '***', rememberMe });
    alert('This is UI demo only. Authentication not configured yet.');
  };

  const handleSocialLogin = (provider) => {
    alert(`${provider} login UI demo - not configured yet.`);
  };

  return (
    <Container>
      {/* Left Panel - Branding */}
      <LeftPanel>
        <Box sx={{ textAlign: 'center', maxWidth: '500px' }}>
          {/* Large Logo */}
          <Box sx={{ mb: 4 }}>
            <Box
              sx={{
                width: '80px',
                height: '80px',
                borderRadius: '20px',
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3
              }}
            >
              <svg width="48" height="48" viewBox="0 0 35 35" fill="none">
                <rect width="35" height="35" rx="8" fill="#fff" />
                <path d="M17.5 10L12 17.5H15.5V25L19.5 25V17.5H23L17.5 10Z" fill="#1e3c72" />
              </svg>
            </Box>
          </Box>

          <Typography variant="h2" sx={{ fontWeight: 700, mb: 2, fontSize: { xs: '2rem', md: '2.5rem' } }}>
            My Application
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.95, fontWeight: 400, lineHeight: 1.6 }}>
            Secure access to your business dashboard. Manage your operations efficiently and stay connected.
          </Typography>

          {/* Feature List */}
          <Stack spacing={2} sx={{ mt: 6, alignItems: 'flex-start', maxWidth: '360px', mx: 'auto' }}>
            {[
              { icon: '🔒', title: 'Secure & Encrypted', desc: 'Your data is protected with enterprise-grade security' },
              { icon: '⚡', title: 'Lightning Fast', desc: 'Optimized performance for seamless experience' },
              { icon: '🌍', title: 'Global Access', desc: 'Access from anywhere, anytime on any device' }
            ].map((feature) => (
              <Box key={feature.title} sx={{ display: 'flex', gap: 2, textAlign: 'left' }}>
                <Box sx={{ fontSize: '24px', flexShrink: 0 }}>{feature.icon}</Box>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9, fontSize: '13px' }}>
                    {feature.desc}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Stack>
        </Box>
      </LeftPanel>

      {/* Right Panel - Login Form */}
      <RightPanel>
        <LoginContainer>
          {/* Small Logo for Mobile */}
          <Box sx={{ mb: 3, display: { xs: 'block', md: 'none' } }}>
            <svg width="120" height="30" viewBox="0 0 140 35" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="2" width="31" height="31" rx="7" fill="#1e3c72" />
              <path d="M17.5 10L12 17.5H15.5V25L19.5 25V17.5H23L17.5 10Z" fill="#FFFFFF" />
              <text
                x="40"
                y="23"
                fontFamily="system-ui, -apple-system, sans-serif"
                fontSize="18"
                fontWeight="600"
                fill="#1a1a1a"
              >
                My App
              </text>
            </svg>
          </Box>

          {/* Heading */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: '#1a1a1a' }}>
              Sign in to your account
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Welcome back! Please enter your details
            </Typography>
          </Box>

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              {/* Email Input */}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#333', fontSize: '14px' }}>
                  Email
                </Typography>
                <StyledTextField
                  fullWidth
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </Box>

              {/* Password Input */}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#333', fontSize: '14px' }}>
                  Password
                </Typography>
                <StyledTextField
                  fullWidth
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                          {showPassword ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                />
              </Box>

              {/* Remember Me & Forgot Password */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <FormControlLabel
                  control={<Checkbox checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} size="small" />}
                  label={<Typography variant="body2">Remember me</Typography>}
                />
                <Link href="#" variant="body2" sx={{ color: '#1e3c72', textDecoration: 'none', fontWeight: 600 }}>
                  Forgot password?
                </Link>
              </Box>

              {/* Sign In Button */}
              <GradientButton type="submit" fullWidth variant="contained" size="large">
                Sign in
              </GradientButton>
            </Stack>
          </form>

          {/* Divider */}
          <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
            <Divider sx={{ flex: 1 }} />
            <Typography variant="caption" sx={{ px: 2, color: '#999' }}>
              Or continue with
            </Typography>
            <Divider sx={{ flex: 1 }} />
          </Box>

          {/* Social Login Buttons */}
          <Stack direction="row" spacing={1.5}>
            <SocialButton onClick={() => handleSocialLogin('Google')}>
              <svg width="18" height="18" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            </SocialButton>

            <SocialButton onClick={() => handleSocialLogin('Microsoft')}>
              <svg width="18" height="18" viewBox="0 0 23 23" fill="none">
                <path d="M0 0h10.933v10.933H0z" fill="#f25022" />
                <path d="M12.067 0H23v10.933H12.067z" fill="#00a4ef" />
                <path d="M0 12.067h10.933V23H0z" fill="#7fba00" />
                <path d="M12.067 12.067H23V23H12.067z" fill="#ffb900" />
              </svg>
            </SocialButton>

            <SocialButton onClick={() => handleSocialLogin('Apple')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
              </svg>
            </SocialButton>
          </Stack>
        </LoginContainer>
      </RightPanel>
    </Container>
  );
}
