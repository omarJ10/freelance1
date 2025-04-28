<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class PredictionLinkedInController extends AbstractController
{

    private $httpClient;

    public function __construct(HttpClientInterface $httpClient)
    {
        $this->httpClient = $httpClient;
    }

    /*#[Route('/linkedin/suggestPost', name: 'app_suggestPost_linkedin')]
    public function suggestPost(Request $request): Response
    {
        // Récupérer le thème depuis le formulaire (ou tout autre input)
        $theme = $request->request->get('theme');

        try {
            // Appeler l'API Flask pour la suggestion de post
            $response = $this->httpClient->request('POST', 'http://127.0.0.1:5003/suggest_post', [
                'json' => ['theme' => $theme]
            ]);

            $data = $response->toArray();

            return $this->render('prediction_linked_in/suggestPost.html.twig', [
                'theme' => $theme,
                'suggestions' => $data['suggestions'] ?? [], // Cette ligne assure que `suggestions` est toujours défini
                'error' => $data['error'] ?? null,
            ]);
        } catch (\Exception $e) {
            return $this->render('prediction_linked_in/suggestPost.html.twig', [
                'theme' => $theme,
                'error' => "Erreur lors de la génération des suggestions : " . $e->getMessage(),
            ]);
        }
    }


    #[Route('/linkedin/predictEngagement', name: 'app_predictEngagement_linkedin')]
    public function predictEngagement(Request $request): Response
    {
        // Récupérer le contenu du post depuis le formulaire
        $postContent = $request->request->get('post_content', '');

        try {
            // Appeler l'API Flask pour la prédiction d'engagement
            $response = $this->httpClient->request('POST', 'http://127.0.0.1:5003/predict_engagement', [
                'json' => ['post_content' => $postContent]
            ]);

            $data = $response->toArray();

            return $this->render('prediction_linked_in/predictEngagement.html.twig', [
                'post_content' => $postContent,
                'predicted_comments' => $data['predicted_comments'] ?? null,
                'predicted_likes' => $data['predicted_likes'] ?? null,
                'predicted_reposts' => $data['predicted_reposts'] ?? null,
                'error' => null

            ]);
        } catch (\Exception $e) {
            return $this->render('prediction_linked_in/predictEngagement.html.twig', [
                'post_content' => $postContent,
                'predicted_comments' => null,
                'predicted_likes' => null,
                'predicted_reposts' => null,
                'error' => "Erreur lors de la prédiction : " . $e->getMessage(),
            ]);
        }
    }

    #[Route('/linkedin/insights', name: 'app_insights_linkedin')]
    public function fetchInsights(): Response
    {
        try {
            $response = $this->httpClient->request('GET', 'http://127.0.0.1:5003/optimal_posting');
            $data = $response->toArray();
            return $this->render('prediction_linked_in/insights.html.twig', [
                'jour_optimal' => $data['jour_optimal'],
                'type_optimal' => $data['type_optimal'],
                'error' => $data['error'] ?? null,
            ]);
        } catch (\Exception $e) {
            return $this->render('prediction_linked_in/insights.html.twig', [
                'error' => "Erreur lors de la récupération des insights : " . $e->getMessage(),
            ]);
        }
    }*/

    #[Route('/linkedin/dashboard', name: 'app_prediction_linkedin')]
    public function index(Request $request): Response
    {
        // Variables pour stocker les résultats des API
        $theme = $request->request->get('theme', '');
        $postContent = $request->request->get('post_content', '');
        $suggestions = [];
        $predictedComments = null;
        $predictedLikes = null;
        $predictedReposts = null;
        $insights = [
            'jour_optimal' => null,
            'type_optimal' => null
        ];
        $error = null;

        try {
            // 1. Appeler l'API Flask pour la suggestion de post
            if ($theme) {
                $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/suggest_post', [
                    'json' => ['theme' => $theme],
                ]);
                $data = $response->toArray();
                $suggestions = $data['suggestions'] ?? [];
            }

            // 2. Appeler l'API Flask pour la prédiction d'engagement
            if ($postContent) {
                $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/predict_engagement', [
                    'json' => ['post_content' => $postContent],
                ]);
                $data = $response->toArray();
                $predictedComments = $data['predicted_comments'] ?? null;
                $predictedLikes = $data['predicted_likes'] ?? null;
                $predictedReposts = $data['predicted_reposts'] ?? null;
            }

            /*// 3. Appeler l'API Flask pour les insights
            $response = $this->httpClient->request('GET', 'http://127.0.0.1:5003/optimal_posting');
            $data = $response->toArray();
            $insights['jour_optimal'] = $data['jour_optimal'] ?? null;
            $insights['type_optimal'] = $data['type_optimal'] ?? null;*/

        } catch (\Exception $e) {
            $error = "Erreur lors de l'exécution : " . $e->getMessage();
        }
        $user = $this->getUser();

        // Retourner les résultats au template Twig
        return $this->render('prediction_linked_in/index.html.twig', [
            'theme' => $theme,
            'username' => $user->getUsername(),
            'suggestions' => $suggestions,
            'post_content' => $postContent,
            'predicted_comments' => $predictedComments,
            'predicted_likes' => $predictedLikes,
            'predicted_reposts' => $predictedReposts,
            /*'jour_optimal' => $insights['jour_optimal'],
            'type_optimal' => $insights['type_optimal'],*/
            'error' => $error,
        ]);
    }


}
