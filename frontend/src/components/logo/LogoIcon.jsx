// material-ui
import { useTheme } from '@mui/material/styles';

/**
 * if you want to use image instead of <svg> uncomment following.
 *
 * import logoIconDark from 'assets/images/logo-icon-dark.svg';
 * import logoIcon from 'assets/images/logo-icon.svg';
 * import { ThemeMode } from 'config';
 *
 */

// ==============================|| LOGO ICON SVG ||============================== //

export default function LogoIcon() {
  const theme = useTheme();

  return (
    /**
     * if you want to use image instead of svg uncomment following, and comment out <svg> element.
     *
     * <img src={theme.palette.mode === ThemeMode.DARK ? logoIconDark : logoIcon} alt="App Icon" width="100" />
     *
     */
    <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Simple rounded square icon with app symbol */}
      <rect x="5" y="5" width="50" height="50" rx="12" fill={theme.palette.primary.main} />
      <rect x="5" y="5" width="50" height="50" rx="12" stroke={theme.palette.primary.dark} strokeWidth="3" />
      <path
        d="M30 18L20 30H26V42H34V30H40L30 18Z"
        fill={theme.palette.common.white}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
