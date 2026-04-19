import Header from './components/Header';
import Footer from './components/Footer';
import RecommendationClient from './components/RecommendationClient';

export default function Home() {
  return (
    <>
      <Header />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <RecommendationClient />
      </main>
      <Footer />
    </>
  );
}
