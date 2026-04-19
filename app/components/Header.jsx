import Link from 'next/link';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logoContainer}>
        <span className={styles.logo}>zomato</span>
        <span className={styles.aiTag}>AI</span>
      </div>
      
      <nav className={styles.nav}>
        <Link href="/" className={`${styles.navLink} ${styles.active}`}>Home</Link>
        <Link href="#" className={styles.navLink}>Dining Out</Link>
        <Link href="#" className={styles.navLink}>Delivery</Link>
        <Link href="#" className={styles.navLink}>Profile</Link>
      </nav>

      <div className={styles.actions}>
        <div className={styles.iconCircle}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
        </div>
        <div className={styles.iconCircle}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
      </div>
    </header>
  );
}
