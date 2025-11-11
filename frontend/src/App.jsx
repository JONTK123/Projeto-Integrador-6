import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Home from './pages/Home';
import Usuarios from './pages/Usuarios';
import Estabelecimentos from './pages/Estabelecimentos';
import Preferencias from './pages/Preferencias';
import Recomendacoes from './pages/Recomendacoes';
import Treinamento from './pages/Treinamento';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="usuarios" element={<Usuarios />} />
            <Route path="estabelecimentos" element={<Estabelecimentos />} />
            <Route path="preferencias" element={<Preferencias />} />
            <Route path="recomendacoes" element={<Recomendacoes />} />
            <Route path="treinamento" element={<Treinamento />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

