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

    #[Route('/linkedin/dashboard', name: 'app_prediction_linkedin')]
    public function index(Request $request): Response
    {
        $theme = $request->request->get('theme', '');
        $postContent = $request->request->get('post_content', '');
        $suggestions = [];
        $predictedComments = null;
        $predictedLikes = null;
        $predictedReposts = null;
        $error = null;

        try {
            if ($theme) {
                $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/suggest_post', [
                    'json' => ['theme' => $theme],
                ]);
                $data = $response->toArray(false);
                $suggestions = $data['suggestions'] ?? [];
            }

            if ($postContent) {
                $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/predict_engagement', [
                    'json' => ['post_content' => $postContent],
                ]);
                $data = $response->toArray(false);
                $predictedComments = $data['predicted_comments'] ?? null;
                $predictedLikes = $data['predicted_likes'] ?? null;
                $predictedReposts = $data['predicted_reposts'] ?? null;
            }
        } catch (\Exception $e) {
            $error = "Erreur lors de l'exécution : " . $e->getMessage();
        }

        //$user = $this->getUser();
        //$username = $user ? $user->getUsername() : null;

        return $this->render('prediction_linked_in/index.html.twig', [
            'theme' => $theme,
            //'username' => $username,
            'suggestions' => $suggestions,
            'post_content' => $postContent,
            'predicted_comments' => $predictedComments,
            'predicted_likes' => $predictedLikes,
            'predicted_reposts' => $predictedReposts,
            'error' => $error,
        ]);
    }
}
