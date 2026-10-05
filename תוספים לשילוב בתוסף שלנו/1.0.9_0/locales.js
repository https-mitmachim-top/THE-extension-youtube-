// YTLyrics Translations with Tutorial System
console.log('🌍 Locales.js loaded');

const LOCALES = {
  en: {
    name: 'English',
    flag: '🇺🇸',
    translations: {
      settings: 'Settings',
      control: 'Control',
      language: 'Language',
      autoShowLyrics: 'Auto-show Lyrics',
      autoShowLyricsDesc: 'Show on ALL videos automatically',
      smartAutoShow: 'Smart Auto-show',
      smartAutoShowDesc: 'Auto-show only for music videos',
      darkMode: 'Dark Mode',
      darkModeDesc: 'Use dark theme',
      recommended: 'RECOMMENDED',
      showLyricsNow: 'Show Lyrics Now',
      searching: 'Searching...',
      refreshingExtension: 'Refreshing extension...',
      pleaseOpenYouTubeVideo: 'Please open a YouTube video!',
      tabRefreshed: 'Tab refreshed!',
      extensionRefreshed: 'Extension refreshed!',
      refreshFailed: 'Refresh failed',
      aiAnalyzingTitle: 'AI analyzing title...',
      lyricsPanelOpened: 'Lyrics panel opened!',
      couldNotDetectSong: 'Could not detect song',
      pleaseRefreshAndTryAgain: 'Please refresh the page and try again',
      smartDetection: 'Smart Detection',
      detectsOfficialMV: 'Detects "Official MV", "Music Video"',
      recognizesVEVO: 'Recognizes "VEVO", "Topic" channels',
      smartPatternMatching: 'Smart pattern matching',
      lessAnnoyingMoreUseful: 'LESS ANNOYING, MORE USEFUL',
      
      // Tutorial tips (3 steps - removed dark mode)
      tutorialShowLyricsNow: 'Click here anytime to instantly show lyrics on YouTube videos',
      tutorialAutoShow: 'Turn this ON to automatically show lyrics on every YouTube video',
      tutorialSmartAutoShow: 'RECOMMENDED: Shows lyrics only on music videos - less annoying!',
      tutorialGotIt: 'Got it',
      tutorialNext: 'Next',
      tutorialSkipTour: 'Skip tour'
    }
  },
  es: {
    name: 'Español',
    flag: '🇪🇸',
    translations: {
      settings: 'Configuración', control: 'Control', language: 'Idioma',
      autoShowLyrics: 'Mostrar Letras Automáticamente',
      autoShowLyricsDesc: 'Mostrar en TODOS los videos automáticamente',
      smartAutoShow: 'Mostrar Automáticamente Inteligente',
      smartAutoShowDesc: 'Mostrar automáticamente solo en videos musicales',
      darkMode: 'Modo Oscuro', darkModeDesc: 'Usar tema oscuro', recommended: 'RECOMENDADO',
      showLyricsNow: 'Mostrar Letras Ahora', searching: 'Buscando...',
      refreshingExtension: 'Actualizando extensión...', pleaseOpenYouTubeVideo: '¡Por favor abre un video de YouTube!',
      tabRefreshed: '¡Pestaña actualizada!', extensionRefreshed: '¡Extensión actualizada!', refreshFailed: 'Actualización fallida',
      aiAnalyzingTitle: 'IA analizando título...', lyricsPanelOpened: '¡Panel de letras abierto!',
      couldNotDetectSong: 'No se pudo detectar la canción', pleaseRefreshAndTryAgain: 'Por favor actualiza la página e inténtalo de nuevo',
      smartDetection: 'Detección Inteligente', detectsOfficialMV: 'Detecta "MV Oficial", "Video Musical"',
      recognizesVEVO: 'Reconoce canales "VEVO", "Topic"', smartPatternMatching: 'Coincidencia de patrones inteligente',
      lessAnnoyingMoreUseful: 'MENOS MOLESTO, MÁS ÚTIL',
      tutorialShowLyricsNow: 'Haz clic aquí para mostrar letras instantáneamente en videos de YouTube',
      tutorialAutoShow: 'Activa esto para mostrar letras automáticamente en cada video',
      tutorialSmartAutoShow: 'RECOMENDADO: Muestra letras solo en videos musicales - ¡menos molesto!',
      tutorialGotIt: 'Entendido', tutorialNext: 'Siguiente', tutorialSkipTour: 'Saltar tutorial'
    }
  },
  ru: {
    name: 'Русский', flag: '🇷🇺',
    translations: {
      settings: 'Настройки', control: 'Управление', language: 'Язык',
      autoShowLyrics: 'Автопоказ текстов', autoShowLyricsDesc: 'Показывать на ВСЕХ видео автоматически',
      smartAutoShow: 'Умный автопоказ', smartAutoShowDesc: 'Автопоказ только для музыкальных видео',
      darkMode: 'Темный режим', darkModeDesc: 'Использовать темную тему', recommended: 'РЕКОМЕНДУЕТСЯ',
      showLyricsNow: 'Показать тексты сейчас', searching: 'Поиск...',
      refreshingExtension: 'Обновление расширения...', pleaseOpenYouTubeVideo: 'Пожалуйста, откройте видео YouTube!',
      tabRefreshed: 'Вкладка обновлена!', extensionRefreshed: 'Расширение обновлено!', refreshFailed: 'Ошибка обновления',
      aiAnalyzingTitle: 'ИИ анализирует название...', lyricsPanelOpened: 'Панель текстов открыта!',
      couldNotDetectSong: 'Не удалось определить песню', pleaseRefreshAndTryAgain: 'Пожалуйста, обновите страницу и попробуйте снова',
      smartDetection: 'Умное определение', detectsOfficialMV: 'Распознает "Official MV", "Music Video"',
      recognizesVEVO: 'Распознает каналы "VEVO", "Topic"', smartPatternMatching: 'Умное сопоставление шаблонов',
      lessAnnoyingMoreUseful: 'МЕНЬШЕ РАЗДРАЖАЕТ, БОЛЬШЕ ПОЛЬЗЫ',
      tutorialShowLyricsNow: 'Нажмите здесь, чтобы мгновенно показать тексты на YouTube',
      tutorialAutoShow: 'Включите это для автоматического показа текстов на каждом видео',
      tutorialSmartAutoShow: 'РЕКОМЕНДУЕТСЯ: Показывает тексты только в музыкальных видео!',
      tutorialGotIt: 'Понятно', tutorialNext: 'Далее', tutorialSkipTour: 'Пропустить'
    }
  },
  ja: {
    name: '日本語', flag: '🇯🇵',
    translations: {
      settings: '設定', control: 'コントロール', language: '言語',
      autoShowLyrics: '自動表示', autoShowLyricsDesc: 'すべての動画で自動表示',
      smartAutoShow: 'スマート自動表示', smartAutoShowDesc: 'ミュージックビデオのみ自動表示',
      darkMode: 'ダークモード', darkModeDesc: 'ダークテーマを使用', recommended: 'おすすめ',
      showLyricsNow: '今すぐ歌詞を表示', searching: '検索中...',
      refreshingExtension: '拡張機能を更新中...', pleaseOpenYouTubeVideo: 'YouTube動画を開いてください！',
      tabRefreshed: 'タブを更新しました！', extensionRefreshed: '拡張機能を更新しました！', refreshFailed: '更新に失敗しました',
      aiAnalyzingTitle: 'AIがタイトルを分析中...', lyricsPanelOpened: '歌詞パネルを開きました！',
      couldNotDetectSong: '曲を検出できませんでした', pleaseRefreshAndTryAgain: 'ページを更新してもう一度お試しください',
      smartDetection: 'スマート検出', detectsOfficialMV: '「Official MV」「Music Video」を検出',
      recognizesVEVO: '「VEVO」「Topic」チャンネルを認識', smartPatternMatching: 'スマートパターンマッチング',
      lessAnnoyingMoreUseful: '邪魔にならず、より便利',
      tutorialShowLyricsNow: 'ここをクリックしてYouTube動画の歌詞を即座に表示',
      tutorialAutoShow: 'これをONにするとすべての動画で歌詞を自動表示します',
      tutorialSmartAutoShow: 'おすすめ：ミュージックビデオのみ歌詞を表示 - 邪魔になりません！',
      tutorialGotIt: 'わかりました', tutorialNext: '次へ', tutorialSkipTour: 'スキップ'
    }
  },
  id: {
    name: 'Bahasa Indonesia', flag: '🇮🇩',
    translations: {
      settings: 'Pengaturan', control: 'Kontrol', language: 'Bahasa',
      autoShowLyrics: 'Tampilkan Lirik Otomatis', autoShowLyricsDesc: 'Tampilkan di SEMUA video secara otomatis',
      smartAutoShow: 'Tampilan Otomatis Pintar', smartAutoShowDesc: 'Tampilkan otomatis hanya untuk video musik',
      darkMode: 'Mode Gelap', darkModeDesc: 'Gunakan tema gelap', recommended: 'DIREKOMENDASIKAN',
      showLyricsNow: 'Tampilkan Lirik Sekarang', searching: 'Mencari...',
      refreshingExtension: 'Memperbarui ekstensi...', pleaseOpenYouTubeVideo: 'Silakan buka video YouTube!',
      tabRefreshed: 'Tab diperbarui!', extensionRefreshed: 'Ekstensi diperbarui!', refreshFailed: 'Pembaruan gagal',
      aiAnalyzingTitle: 'AI menganalisis judul...', lyricsPanelOpened: 'Panel lirik dibuka!',
      couldNotDetectSong: 'Tidak dapat mendeteksi lagu', pleaseRefreshAndTryAgain: 'Silakan perbarui halaman dan coba lagi',
      smartDetection: 'Deteksi Pintar', detectsOfficialMV: 'Mendeteksi "Official MV", "Music Video"',
      recognizesVEVO: 'Mengenali saluran "VEVO", "Topic"', smartPatternMatching: 'Pencocokan pola pintar',
      lessAnnoyingMoreUseful: 'LEBIH BERGUNA, TIDAK MENGGANGGU',
      tutorialShowLyricsNow: 'Klik di sini untuk langsung menampilkan lirik di video YouTube',
      tutorialAutoShow: 'Aktifkan ini untuk menampilkan lirik otomatis di setiap video',
      tutorialSmartAutoShow: 'DIREKOMENDASIKAN: Tampilkan lirik hanya di video musik - tidak mengganggu!',
      tutorialGotIt: 'Mengerti', tutorialNext: 'Lanjut', tutorialSkipTour: 'Lewati tutorial'
    }
  },
  ko: {
    name: '한국어', flag: '🇰🇷',
    translations: {
      settings: '설정', control: '제어', language: '언어',
      autoShowLyrics: '가사 자동 표시', autoShowLyricsDesc: '모든 동영상에 자동으로 표시',
      smartAutoShow: '스마트 자동 표시', smartAutoShowDesc: '뮤직비디오에만 자동 표시',
      darkMode: '다크 모드', darkModeDesc: '다크 테마 사용', recommended: '권장',
      showLyricsNow: '지금 가사 표시', searching: '검색 중...',
      refreshingExtension: '확장 프로그램 새로고침 중...', pleaseOpenYouTubeVideo: 'YouTube 동영상을 열어주세요!',
      tabRefreshed: '탭이 새로고침되었습니다!', extensionRefreshed: '확장 프로그램이 새로고침되었습니다!', refreshFailed: '새로고침 실패',
      aiAnalyzingTitle: 'AI가 제목을 분석하는 중...', lyricsPanelOpened: '가사 패널이 열렸습니다!',
      couldNotDetectSong: '노래를 감지할 수 없습니다', pleaseRefreshAndTryAgain: '페이지를 새로고침하고 다시 시도해주세요',
      smartDetection: '스마트 감지', detectsOfficialMV: '"Official MV", "뮤직비디오" 감지',
      recognizesVEVO: '"VEVO", "Topic" 채널 인식', smartPatternMatching: '스마트 패턴 매칭',
      lessAnnoyingMoreUseful: '덜 방해되고, 더 유용함',
      tutorialShowLyricsNow: '여기를 클릭하여 YouTube 동영상에서 가사를 즉시 표시',
      tutorialAutoShow: '이 기능을 켜면 모든 동영상에서 자동으로 가사를 표시합니다',
      tutorialSmartAutoShow: '권장: 뮤직비디오에서만 가사를 표시 - 방해되지 않습니다!',
      tutorialGotIt: '알겠습니다', tutorialNext: '다음', tutorialSkipTour: '건너뛰기'
    }
  },
  pt: {
    name: 'Português', flag: '🇧🇷',
    translations: {
      settings: 'Configurações', control: 'Controle', language: 'Idioma',
      autoShowLyrics: 'Mostrar Letras Automaticamente', autoShowLyricsDesc: 'Mostrar em TODOS os vídeos automaticamente',
      smartAutoShow: 'Mostrar Automaticamente Inteligente', smartAutoShowDesc: 'Mostrar automaticamente apenas em vídeos musicais',
      darkMode: 'Modo Escuro', darkModeDesc: 'Usar tema escuro', recommended: 'RECOMENDADO',
      showLyricsNow: 'Mostrar Letras Agora', searching: 'Buscando...',
      refreshingExtension: 'Atualizando extensão...', pleaseOpenYouTubeVideo: 'Por favor, abra um vídeo do YouTube!',
      tabRefreshed: 'Aba atualizada!', extensionRefreshed: 'Extensão atualizada!', refreshFailed: 'Atualização falhou',
      aiAnalyzingTitle: 'IA analisando título...', lyricsPanelOpened: 'Painel de letras aberto!',
      couldNotDetectSong: 'Não foi possível detectar a música', pleaseRefreshAndTryAgain: 'Por favor, atualize a página e tente novamente',
      smartDetection: 'Detecção Inteligente', detectsOfficialMV: 'Detecta "MV Oficial", "Vídeo Musical"',
      recognizesVEVO: 'Reconhece canais "VEVO", "Topic"', smartPatternMatching: 'Correspondência de padrões inteligente',
      lessAnnoyingMoreUseful: 'MENOS IRRITANTE, MAIS ÚTIL',
      tutorialShowLyricsNow: 'Clique aqui para mostrar letras instantaneamente em vídeos do YouTube',
      tutorialAutoShow: 'Ative isso para mostrar letras automaticamente em cada vídeo',
      tutorialSmartAutoShow: 'RECOMENDADO: Mostra letras apenas em vídeos musicais - menos irritante!',
      tutorialGotIt: 'Entendi', tutorialNext: 'Próximo', tutorialSkipTour: 'Pular tour'
    }
  }
};

function t(key, lang = 'en') {
  const locale = LOCALES[lang] || LOCALES.en;
  return locale.translations[key] || LOCALES.en.translations[key] || key;
}

function detectBrowserLanguage() {
  const browserLang = navigator.language.toLowerCase();
  console.log('🌍 Browser language:', browserLang);
  const shortLang = browserLang.split('-')[0];
  if (LOCALES[shortLang]) return shortLang;
  if (browserLang.startsWith('pt')) return 'pt';
  if (browserLang.startsWith('zh')) return 'zh';
  return 'en';
}

function getAvailableLanguages() {
  return Object.entries(LOCALES).map(([code, data]) => ({
    code, name: data.name, flag: data.flag
  }));
}

if (typeof window !== 'undefined') {
  window.LOCALES = LOCALES;
  window.t = t;
  window.detectBrowserLanguage = detectBrowserLanguage;
  window.getAvailableLanguages = getAvailableLanguages;
}