import { createContext, useEffect, useReducer } from 'react';

// third-party
import { Chance } from 'chance';
import { jwtDecode } from 'jwt-decode';

// reducer - state management
import { LOGIN, LOGOUT } from 'contexts/auth-reducer/actions';
import authReducer from 'contexts/auth-reducer/auth';

// project imports
import Loader from 'components/Loader';
import axios from 'utils/axios';

const chance = new Chance();

// constant
const initialState = {
  isLoggedIn: false,
  isInitialized: false,
  user: null
};

const verifyToken = (serviceToken) => {
  if (!serviceToken) {
    return false;
  }
  const decoded = jwtDecode(serviceToken);
  /**
   * Property 'exp' does not exist on type '<T = unknown>(token: string, options?: JwtDecodeOptions | undefined) => T'.
   */
  return decoded.exp > Date.now() / 1000;
};

const setSession = (serviceToken) => {
  if (serviceToken) {
    localStorage.setItem('serviceToken', serviceToken);
    axios.defaults.headers.common.Authorization = `Bearer ${serviceToken}`;
  } else {
    localStorage.removeItem('serviceToken');
    delete axios.defaults.headers.common.Authorization;
  }
};

// ==============================|| JWT CONTEXT & PROVIDER ||============================== //

const JWTContext = createContext(null);

export const JWTProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const init = async () => {
      try {
        const serviceToken = window.localStorage.getItem('serviceToken');
        if (serviceToken && verifyToken(serviceToken)) {
          setSession(serviceToken);

          // Try to get stored user data first (from OAuth callback)
          const storedUser = window.localStorage.getItem('user');
          let user;

          if (storedUser) {
            // Use stored user data (has complete profile info)
            user = JSON.parse(storedUser);
          } else {
            // Fallback: decode token to get basic user info
            const decoded = jwtDecode(serviceToken);
            user = {
              id: decoded.sub,
              email: decoded.email,
              username: decoded.username,
              name: decoded.username || decoded.email
            };
          }

          dispatch({
            type: LOGIN,
            payload: {
              isLoggedIn: true,
              user
            }
          });
        } else {
          dispatch({
            type: LOGOUT
          });
        }
      } catch (err) {
        console.error(err);
        dispatch({
          type: LOGOUT
        });
      }
    };

    init();
  }, []);

  const login = async (email, password, recaptchaToken = null) => {
    const response = await axios.post('/api/v1/auth/login', {
      email,
      password,
      recaptcha_token: recaptchaToken
    });
    const { access_token, user, requires_mfa, mfa_token, mfa_method, available_mfa_methods } = response.data;

    // Check if MFA is required
    if (requires_mfa && mfa_token) {
      // Return MFA info to the caller
      return {
        requires_mfa: true,
        mfa_token,
        mfa_method,
        available_mfa_methods
      };
    }

    // Normal login flow (no MFA or MFA disabled)
    setSession(access_token);
    dispatch({
      type: LOGIN,
      payload: {
        isLoggedIn: true,
        user
      }
    });

    return {
      requires_mfa: false,
      user
    };
  };

  const verifyMFA = async (mfa_token, passcode = null) => {
    const response = await axios.post('/api/v1/auth/mfa/verify', {
      mfa_token,
      passcode
    });

    const { status, message, access_token, refresh_token, user } = response.data;

    if (status === 'approved' && access_token) {
      // MFA approved - complete login
      setSession(access_token);

      if (refresh_token) {
        localStorage.setItem('refreshToken', refresh_token);
      }

      // Store user data
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      }

      dispatch({
        type: LOGIN,
        payload: {
          isLoggedIn: true,
          user
        }
      });

      return { status: 'approved', user };
    }

    // Return status for pending, denied, or error
    return { status, message };
  };

  const register = async (email, password, firstName, lastName) => {
    // todo: this flow need to be recode as it not verified
    const id = chance.bb_pin();
    const response = await axios.post('/api/account/register', {
      id,
      email,
      password,
      firstName,
      lastName
    });
    let users = response.data;

    if (window.localStorage.getItem('users') !== undefined && window.localStorage.getItem('users') !== null) {
      const localUsers = window.localStorage.getItem('users');
      users = [
        ...JSON.parse(localUsers),
        {
          id,
          email,
          password,
          name: `${firstName} ${lastName}`
        }
      ];
    }

    window.localStorage.setItem('users', JSON.stringify(users));
  };

  const logout = () => {
    setSession(null);
    localStorage.removeItem('user');
    localStorage.removeItem('refreshToken');
    dispatch({ type: LOGOUT });
  };

  const resetPassword = async (email) => {
    console.log('email - ', email);
  };

  const updateProfile = () => {};

  const handleOAuthSession = (sessionData) => {
    // Handle OAuth session - called from OAuth callback
    if (sessionData && sessionData.accessToken) {
      setSession(sessionData.accessToken);

      // Store refresh token if provided
      if (sessionData.refreshToken) {
        localStorage.setItem('refreshToken', sessionData.refreshToken);
      }

      // Dispatch login action with user data
      dispatch({
        type: LOGIN,
        payload: {
          isLoggedIn: true,
          user: sessionData.user
        }
      });
    }
  };

  if (state.isInitialized !== undefined && !state.isInitialized) {
    return <Loader />;
  }

  return (
    <JWTContext.Provider
      value={{
        ...state,
        login,
        logout,
        register,
        resetPassword,
        updateProfile,
        verifyMFA,
        setSession: handleOAuthSession
      }}
    >
      {children}
    </JWTContext.Provider>
  );
};

export default JWTContext;
