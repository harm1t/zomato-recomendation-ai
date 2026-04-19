import styles from './Footer.module.css';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.logoRow}>
          <span className={styles.logo}>zomato</span>
          <span className={styles.aiTag}>AI</span>
        </div>
        <div className={styles.links}>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">AI Methodology</a>
          <a href="#">Contact</a>
        </div>
      </div>
      <div className={styles.copyright}>
        © 2026 The Intelligent Epicurean. An AI-Driven Gastronomic Concierge powered by Zomato.
      </div>
    </footer>
  );
}
