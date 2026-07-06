/**
 * Genre English → Arabic translation map.
 * 
 * The API stores genres in English. This map provides
 * clean Arabic labels for the public-facing UI.
 * The English key is used for API filtering; only the display is translated.
 */

const GENRE_MAP = {
  'Action': 'أكشن',
  'Adventure': 'مغامرات',
  'Animation': 'رسوم متحركة',
  'Comedy': 'كوميديا',
  'Crime': 'جريمة',
  'Documentary': 'وثائقي',
  'Drama': 'دراما',
  'Family': 'عائلي',
  'Fantasy': 'فانتازيا',
  'History': 'تاريخي',
  'Horror': 'رعب',
  'Music': 'موسيقي',
  'Mystery': 'غموض',
  'Romance': 'رومانسي',
  'Science Fiction': 'خيال علمي',
  'TV Movie': 'فيلم تلفزيوني',
  'Thriller': 'إثارة',
  'War': 'حربي',
  'Western': 'ويسترن',
};

/**
 * Translate a single genre name to Arabic.
 * Falls back to the original name if no translation exists.
 */
export function translateGenre(name) {
  return GENRE_MAP[name] || name;
}

/**
 * Translate an array of genre names to Arabic.
 */
export function translateGenres(genres) {
  if (!Array.isArray(genres)) return [];
  return genres.map(translateGenre);
}

export default GENRE_MAP;
