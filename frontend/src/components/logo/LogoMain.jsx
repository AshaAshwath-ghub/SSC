import PropTypes from 'prop-types';
// material-ui
import { useTheme } from '@mui/material/styles';

// project imports
import { ThemeMode } from 'config';

/**
 * if you want to use image instead of <svg> uncomment following.
 *
 * import logoDark from 'assets/images/logo-dark.svg';
 * import logo from 'assets/images/logo.svg';
 *
 */

// ==============================|| LOGO SVG ||============================== //

export default function LogoMain({ reverse }) {
  const theme = useTheme();
  return (
    /**
     * if you want to use image instead of svg uncomment following, and comment out <svg> element.
     *
     * <img src={theme.palette.mode === ThemeMode.DARK ? logoDark : logo} alt="App Logo" width="100" />
     *
     */
    <>
      <svg width="140" height="35" viewBox="0 0 140 35" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Simple App Icon */}
        <rect x="2" y="2" width="31" height="31" rx="7" fill={theme.palette.primary.main} />
        <rect x="2" y="2" width="31" height="31" rx="7" stroke={theme.palette.primary.dark} strokeWidth="2" />
        <path
          d="M17.5 10L12 17.5H15.5V25L19.5 25V17.5H23L17.5 10Z"
          fill={theme.palette.common.white}
        />
        {/* App Name Text */}
        <text
          x="40"
          y="23"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="18"
          fontWeight="600"
          fill={theme.palette.mode === ThemeMode.DARK || reverse ? theme.palette.common.white : theme.palette.common.black}
          fillOpacity="0.85"
        >
          My App
        </text>
      </svg>
    </>
  );
}

LogoMain.propTypes = { reverse: PropTypes.bool };
