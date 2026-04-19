import styles from './RestaurantCard.module.css';

const FOOD_IMAGES = [
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
  "https://images.unsplash.com/photo-1514326640560-7d063ef2aed5",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",
  "https://images.unsplash.com/photo-1490645935967-10de6ba17061"
];

export default function RestaurantCard({ item, index }) {
  const imageUrl = FOOD_IMAGES[index % FOOD_IMAGES.length] + "?q=80&w=800&auto=format&fit=crop";
  const costStr = item.cost_display || item.estimated_cost || "—";
  const rating = item.rating ? Number(item.rating).toFixed(1) : "—";
  
  return (
    <div className={styles.card}>
      <div className={styles.imageCol}>
        <img src={imageUrl} alt={item.name} className={styles.image} />
      </div>
      
      <div className={styles.contentCol}>
        <div className={styles.headerRow}>
          <h3 className={styles.name}>{item.name}</h3>
          <div className={styles.ratingBadge}>
            {rating} ★
          </div>
        </div>
        
        <div className={styles.metaRow}>
          <span className={styles.cuisines}>{item.cuisines?.join(', ')}</span>
          <span className={styles.bullet}>•</span>
          <span className={styles.cost}>{costStr}</span>
        </div>
        
        <div className={styles.aiBox}>
          <div className={styles.aiHeader}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.robotIcon}><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>
            <span className={styles.aiLabel}>AI Reason:</span>
          </div>
          <p className={styles.explanation}>{item.explanation}</p>
        </div>
      </div>
    </div>
  );
}
