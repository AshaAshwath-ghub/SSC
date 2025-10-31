import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

// project imports
import useAuth from 'hooks/useAuth';

// ================================|| OAUTH CALLBACK ||================================ //

export default function OAuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setSession, isLoggedIn } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Prevent duplicate processing
      if (hasProcessed.current) return;

      try {
        console.log('OAuth callback started');

        // Get tokens from URL parameters
        const accessToken = searchParams.get('access_token');
        const refreshToken = searchParams.get('refresh_token');
        const userId = searchParams.get('user_id');
        const email = searchParams.get('email');
        const username = searchParams.get('username');
        const firstName = searchParams.get('first_name');
        const lastName = searchParams.get('last_name');

        console.log('OAuth callback params:', {
          hasAccessToken: !!accessToken,
          hasRefreshToken: !!refreshToken,
          userId,
          email,
          username,
          firstName,
          lastName
        });

        if (!accessToken || !refreshToken) {
          console.error('OAuth callback: Missing tokens');
          navigate('/login', { replace: true });
          return;
        }

        // Store tokens in localStorage
        localStorage.setItem('serviceToken', accessToken);
        if (refreshToken) {
          localStorage.setItem('refreshToken', refreshToken);
        }

        // Store user info
        const user = {
          id: userId,
          email,
          username: username || email.split('@')[0],
          name: `${firstName || ''} ${lastName || ''}`.trim() || username || email.split('@')[0],
          first_name: firstName || '',
          last_name: lastName || ''
        };

        console.log('Storing user:', user);
        localStorage.setItem('user', JSON.stringify(user));

        // Update auth context if it has setSession
        if (setSession && typeof setSession === 'function') {
          console.log('Updating auth context');
          setSession({ accessToken, refreshToken, user });
          hasProcessed.current = true;
        }
      } catch (error) {
        console.error('OAuth callback error:', error);
        navigate('/login', { replace: true });
      }
    };

    handleCallback();
  }, [searchParams, navigate, setSession]);

  // Wait for auth state to update, then navigate
  useEffect(() => {
    if (isLoggedIn && hasProcessed.current) {
      console.log('Auth state updated, redirecting to dashboard');
      navigate('/dashboard/default', { replace: true });
    }
  }, [isLoggedIn, navigate]);

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div>
        <h3>Processing OAuth login...</h3>
        <p>Please wait while we complete your authentication.</p>
      </div>
    </div>
  );
}
