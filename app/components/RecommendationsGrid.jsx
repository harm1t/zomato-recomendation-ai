import RestaurantCard from './RestaurantCard';
import styles from './RecommendationsGrid.module.css';

export default function RecommendationsGrid({ items }) {
  if (!items || items.length === 0) {
    return <p className={styles.empty}>No restaurants found. Try adjusting your preferences.</p>;
  }

  return (
    <div className={styles.grid}>
      {items.map((item, index) => (
        <RestaurantCard key={item.id} item={item} index={index} />
      ))}
    </div>
  );
}
